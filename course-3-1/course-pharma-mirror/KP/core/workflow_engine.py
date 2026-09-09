from typing import Dict, List, Any, Callable, Optional, Union
import asyncio
import logging
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowResult:
    workflow_id: str
    state: WorkflowState
    results: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    execution_log: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.execution_log is None:
            self.execution_log = []

    @property
    def duration(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def add_log_entry(self, node_name: str, result: Any, error: Optional[str] = None):
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "node": node_name,
            "result": result,
            "error": error
        })


class WorkflowNode:
    def __init__(self,
                 name: str,
                 agent: Any,
                 description: str = "",
                 conditions: Optional[List[Callable]] = None,
                 timeout: int = 1600,
                 retries: int = 2):
        self.name = name
        self.agent = agent
        self.description = description
        self.conditions = conditions or []
        self.timeout = timeout
        self.retries = retries
        self.result = None

    async def execute(self, context: Any) -> Dict[str, Any]:
        logger.info(f"Executing node: {self.name}")

        for condition in self.conditions:
            if not condition(context):
                logger.info(f"Node {self.name} skipped - condition not met")
                return {
                    "node": self.name,
                    "status": "skipped",
                    "reason": "condition_not_met",
                    "timestamp": datetime.now().isoformat()
                }

        for attempt in range(self.retries + 1):
            try:
                logger.debug(f"Node {self.name} attempt {attempt + 1}/{self.retries + 1}")

                task = asyncio.create_task(self.agent(context))

                result = await asyncio.wait_for(task, timeout=self.timeout)

                self.result = result

                logger.info(f"Node {self.name} completed successfully")

                return {
                    "node": self.name,
                    "status": "completed",
                    "result": result,
                    "attempts": attempt + 1,
                    "timestamp": datetime.now().isoformat()
                }

            except asyncio.TimeoutError:
                logger.error(f"Node {self.name} timed out (attempt {attempt + 1})")
                if attempt == self.retries:
                    return {
                        "node": self.name,
                        "status": "failed",
                        "error": f"Timeout after {self.timeout}s",
                        "timestamp": datetime.now().isoformat()
                    }

            except Exception as e:
                logger.error(f"Node {self.name} failed (attempt {attempt + 1}): {e}", exc_info=True)
                if attempt == self.retries:
                    return {
                        "node": self.name,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }

            if attempt < self.retries:
                await asyncio.sleep(1 * (attempt + 1))

        return {
            "node": self.name,
            "status": "failed",
            "error": "Max retries exceeded",
            "timestamp": datetime.now().isoformat()
        }


class ParallelWorkflowNode:
    def __init__(self, name: str, nodes: List[WorkflowNode], description: str = ""):
        self.name = name
        self.nodes = nodes
        self.description = description

    async def execute(self, context: Any) -> Dict[str, Any]:
        logger.info(f"Executing parallel node: {self.name} with {len(self.nodes)} subnodes")

        tasks = [node.execute(context) for node in self.nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated_result = {
            "node": self.name,
            "type": "parallel",
            "subnode_count": len(self.nodes),
            "subnode_results": [],
            "timestamp": datetime.now().isoformat()
        }

        failed_nodes = []
        successful_nodes = []

        for i, result in enumerate(results):
            node_name = self.nodes[i].name

            if isinstance(result, Exception):
                node_result = {
                    "node": node_name,
                    "status": "failed",
                    "error": str(result)
                }
                failed_nodes.append(node_name)
            else:
                node_result = result
                if result.get("status") == "completed":
                    successful_nodes.append(node_name)
                elif result.get("status") == "failed":
                    failed_nodes.append(node_name)

            aggregated_result["subnode_results"].append(node_result)

        if failed_nodes:
            aggregated_result["status"] = "partial_failure"
            aggregated_result["failed_nodes"] = failed_nodes
            aggregated_result["successful_nodes"] = successful_nodes
        else:
            aggregated_result["status"] = "completed"

        logger.info(
            f"Parallel node {self.name} completed: {len(successful_nodes)} successful, {len(failed_nodes)} failed")

        return aggregated_result


class SequentialWorkflowNode:
    def __init__(self, name: str, nodes: List[WorkflowNode], description: str = ""):
        self.name = name
        self.nodes = nodes
        self.description = description

    async def execute(self, context: Any) -> Dict[str, Any]:
        logger.info(f"Executing sequential node: {self.name} with {len(self.nodes)} subnodes")

        results = {
            "node": self.name,
            "type": "sequential",
            "subnode_results": [],
            "timestamp": datetime.now().isoformat()
        }

        for node in self.nodes:
            node_result = await node.execute(context)
            results["subnode_results"].append(node_result)

            if node_result.get("status") in ["failed", "partial_failure"]:
                results["status"] = "interrupted"
                results["last_node"] = node.name
                logger.warning(f"Sequential node {self.name} interrupted at {node.name}")
                break

            if node_result.get("status") == "completed" and "result" in node_result:
                context.update(node_result["result"])

        if "status" not in results:
            results["status"] = "completed"

        logger.info(f"Sequential node {self.name} completed with status: {results['status']}")

        return results


class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, List] = {}
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.logger = logging.getLogger("workflow.engine")

    def register_workflow(self, name: str, workflow_nodes: List):
        self.workflows[name] = workflow_nodes
        self.logger.info(f"Registered workflow: '{name}' with {len(workflow_nodes)} nodes")

    def get_workflow(self, name: str) -> Optional[List]:
        return self.workflows.get(name)

    async def execute_workflow(self,
                               workflow_name: str,
                               context: Any,
                               workflow_id: Optional[str] = None) -> WorkflowResult:

        logger.info(f"📋 Starting workflow '{workflow_name}' with context type: {type(context)}")
        logger.info(f"   Context has symptoms: {hasattr(context, 'symptom_texts')}")
        if hasattr(context, 'symptom_texts'):
            logger.info(f"   Symptoms: {context.symptom_texts}")

        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow_id = workflow_id or f"{workflow_name}_{datetime.now().timestamp()}"

        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            state=WorkflowState.RUNNING,
            results={},
            start_time=datetime.now(),
            execution_log=[]
        )

        self.active_workflows[workflow_id] = workflow_result
        self.logger.info(f"Starting workflow: '{workflow_name}' (ID: {workflow_id})")

        nodes = self.workflows[workflow_name]

        if hasattr(context, 'workflow_id'):
            context.workflow_id = workflow_id
        elif isinstance(context, dict):
            context['workflow_id'] = workflow_id

        try:
            for node in nodes:
                logger.info(f"   🔨 Executing node: {node.name}")
                logger.info(f"   🤖 Node agent type: {type(node.agent)}")
                logger.info(f"   🔍 Node has __call__: {hasattr(node.agent, '__call__')}")

                node_start = datetime.now()

                try:
                    if node.agent is None:
                        logger.error(f"   ❌ Node {node.name} has no agent!")
                        continue

                    node_result = await node.execute(context)
                    logger.info(f"   ✅ Node {node.name} result: {node_result.get('status')}")

                    if node_result.get("status") in ["failed", "partial_failure"]:
                        workflow_result.state = WorkflowState.FAILED
                        workflow_result.error = f"Node {node.name} failed: {node_result.get('error')}"
                        self.logger.error(f"Workflow failed at node: {node.name}")
                        break

                    if node_result.get("status") == "completed" and "result" in node_result:
                        workflow_result.results.update(node_result["result"])

                        if node_result["result"]:
                            try:
                                if hasattr(context, 'update'):
                                    if isinstance(node_result["result"], dict):
                                        context.update(**node_result["result"])
                                    else:
                                        self.logger.warning(f"Node {node.name} result is not a dict")
                                elif isinstance(context, dict):
                                    context.update(node_result["result"])
                                else:
                                    self.logger.warning(f"Cannot update context of type {type(context)}")
                            except Exception as update_error:
                                self.logger.error(f"Failed to update context from node {node.name}: {update_error}")

                    node_duration = (datetime.now() - node_start).total_seconds()
                    self.logger.debug(f"Node {node.name} completed in {node_duration:.2f}s")

                except Exception as e:
                    self.logger.error(f"Error executing node {node.name}: {e}", exc_info=True)
                    workflow_result.state = WorkflowState.FAILED
                    workflow_result.error = f"Node {node.name} error: {str(e)}"
                    workflow_result.add_log_entry(node.name, None, str(e))
                    break

            if workflow_result.state == WorkflowState.RUNNING:
                workflow_result.state = WorkflowState.COMPLETED
                self.logger.info(f"Workflow '{workflow_name}' completed successfully")

        except Exception as e:
            workflow_result.state = WorkflowState.FAILED
            workflow_result.error = f"Workflow execution error: {str(e)}"
            self.logger.error(f"Workflow execution failed: {e}", exc_info=True)

        finally:
            workflow_result.end_time = datetime.now()
            duration = workflow_result.duration
            self.logger.info(
                f"Workflow '{workflow_name}' finished in {duration:.2f}s with state: {workflow_result.state}")

            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

        return workflow_result

    async def execute_with_breakpoints(self,
                                       workflow_name: str,
                                       context: Any,
                                       breakpoints: List[str]) -> Dict[str, Any]:
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        self.logger.info(f"Executing workflow '{workflow_name}' with breakpoints: {breakpoints}")

        nodes = self.workflows[workflow_name]
        results = {}
        stop_at_breakpoint = False

        for node in nodes:
            node_name = node.name

            if node_name in breakpoints:
                self.logger.info(f"Reached breakpoint: {node_name}")
                stop_at_breakpoint = True
                break

            try:
                node_result = await node.execute(context)

                if node_result.get("status") == "completed" and "result" in node_result:
                    results.update(node_result["result"])
                    context.update(node_result["result"])

                if node_result.get("status") in ["failed", "partial_failure"]:
                    self.logger.error(f"Stopping at failed node: {node_name}")
                    break

            except Exception as e:
                self.logger.error(f"Error at node {node_name}: {e}")
                break

        return {
            "completed_nodes": list(results.keys()),
            "results": results,
            "stopped_at_breakpoint": stop_at_breakpoint,
            "context": context.to_dict() if hasattr(context, 'to_dict') else context
        }

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        return self.active_workflows.get(workflow_id)

    def list_workflows(self) -> List[str]:
        return list(self.workflows.keys())

    def cancel_workflow(self, workflow_id: str):
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id].state = WorkflowState.CANCELLED
            self.logger.info(f"Cancelled workflow: {workflow_id}")