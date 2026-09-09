#include <iostream>

#include <sc-memory/sc_memory.hpp>
#include <sc-memory/sc_stream.hpp>
#include <sc-memory/sc_template_search.cpp>

#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>

#include "IsomorphicSearchAgent.hpp"
#include "factory/InferenceManagerFactory.hpp"

using namespace std;
using namespace utils;
using namespace inference;

namespace flightsMod
{
SC_AGENT_IMPLEMENTATION(flightsAgent)
{
  SC_LOG_DEBUG("IsomorphicSearchAgent: started");
 
  ScAddr ruleSet = m_memoryCtx.HelperResolveSystemIdtf("rule_set");
  ScAddr inputStructure = m_memoryCtx.HelperResolveSystemIdtf("input_structure");

  ScAddr const & outputStructure m_memoryCtx.CreateNode(ScType::NodeConstStruct);
  InferenceParams const & inferenceParams{
    ruleSet, {}, {inputStructure}, outputStructure};
  
  InferenceConfig const & inferenceConfig{
    GENERATE_ALL_FORMULAS,
    REPLACEMENTS_ALL,
    TREE_ONLY_OUTPUT_STRUCTURE,
    SEARCH_IN_STRUCTURES};
std::unique_ptr<InferenceManagerAbstract> inferenceManager =
    InferenceManagerFactory::constructDirectInferenceManagerAll(&m_memoryCtx, inferenceConfig);


  bool targetAchieved = inferenceManager->applyInference(inferenceParams);  
  //ScAddr answer =
  inferenceManager->getSolutionTreeManager()->createSolution(outputStructure,targetAchieved);
  utils::AgentUtils::finishAgentWork(&m_memoryCtx, otherAddr, true);

  return SC_RESULT_OK;
}




}  // namespace exampleModule
