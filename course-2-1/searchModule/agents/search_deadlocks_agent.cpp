#include "search_deadlocks_agent.hpp"
#include "keynodes/search_keynodes.hpp"

ScAddr SearchDeadlocksAgent::GetActionClass() const
{
    return SearchKeynodes::action_search_deadlocks;
}

ScResult SearchDeadlocksAgent::Run(ScAddr const & addr, ScAddr const & edgeAddr)
{
    ScAddr graphAddr = addr;
    if (!m_memoryCtx->IsElement(graphAddr)) {
        SC_AGENT_LOG_ERROR("Graph is not specified");
        return SC_RESULT_ERROR;
    }

    ScStructure structure(m_memoryCtx);

    ScIterator3Ptr it3 = m_memoryCtx->CreateIterator3(
        graphAddr,
        ScType::ConstPermPosArc,
        ScType::ConstNode
    );

    while (it3->Next())
    {
        ScAddr node = it3->Get(2);
        if (IsDeadlock(node))
        {
            ScAddr const arcCommonAddr = m_memoryCtx->GenerateConnector(ScType::ConstPermPosArc, SearchKeynodes::deadlock, node);
            structure.Append(arcCommonAddr);
        }
        else if (IsAntiDeadlock(node))
        {
            ScAddr const arcCommonAddr = m_memoryCtx->GenerateConnector(ScType::ConstPermPosArc, SearchKeynodes::anti_deadlock, node);
            structure.Append(arcCommonAddr);
        }
    }

    m_memoryCtx->CreateEdge(ScType::ConstPermPosArc, addr, structure.GetAddr());
    return SC_RESULT_OK;
}

bool SearchDeadlocksAgent::IsDeadlock(const ScAddr &node)
{
    ScIterator3Ptr it3 = m_memoryCtx->CreateIterator3(
        node,
        ScType::ConstCommonEdge,
        ScType::ConstNode
    );
    return !it3->Next();
}

bool SearchDeadlocksAgent::IsAntiDeadlock(const ScAddr &node)
{
    ScIterator3Ptr it3 = m_memoryCtx->CreateIterator3(
        ScType::ConstNode,
        ScType::ConstCommonEdge,
        node
    );
    return !it3->Next();
}