#include "search_deadlocks_agent.hpp"
#include "keynodes/search_keynodes.hpp"

ScAddr DeadendAgent::GetActionClass() const
{
    return DeadendKeynodes::action_find_deadends;
}

ScResult DeadendAgent::Run(ScAddr const & addr, ScAddr const & edgeAddr)
{
    if (!m_ctx->IsElement(addr))
    {
        SC_AGENT_LOG_ERROR("Graph is not specified");
        return SC_RESULT_ERROR;
    }

    // Инициализация ScStructure с контекстом и адресом
    ScStructure structure(*m_ctx, addr);

    FindDeadendsAndAntideadends(addr, structure);

    if (structure.IsEmpty())
    {
        return SC_RESULT_UNKNOWN;
    }

    // Предположим, что нужно создать край с последним элементом структуры
    // Если метод GetLast() отсутствует, используйте другой способ получения последнего элемента
    ScAddr lastElement;
    // Предполагается, что метод GetLast(ScAddr &) существует. Если нет, реализуйте его или используйте другой способ.
    if (!structure.GetLast(lastElement))
    {
        SC_AGENT_LOG_ERROR("Failed to get last element from structure");
        return SC_RESULT_ERROR;
    }

    ScAddr resultEdge = m_ctx->CreateEdge(
        ScType::ConstPermPosArc,
        addr,
        lastElement
    );

    if (!resultEdge.IsValid())
    {
        return SC_RESULT_ERROR;
    }

    return SC_RESULT_OK;
}

void DeadendAgent::FindDeadendsAndAntideadends(const ScAddr & graphNode, ScStructure & structure)
{
    // Узлы классов "Deadend_vertex" и "Antideadend_vertex"
    ScAddr deadendVertexClass = DeadendKeynodes::concept_deadend_vertex;
    ScAddr antideadendVertexClass = DeadendKeynodes::concept_antideadend_vertex;

    if (!deadendVertexClass.IsValid() || !antideadendVertexClass.IsValid())
    {
        SC_AGENT_LOG_ERROR("Keynodes are not initialized");
        return;
    }

    // Итерация по вершинам графа
    ScIterator3Ptr vertexIter = m_ctx->Iterator3(
        graphNode,
        ScType::ConstPermPosArc,
        ScType::ConstNode
    );

    while (vertexIter->Next())
    {
        ScAddr candidateNode = vertexIter->Get(2);
        if (candidateNode == m_ctx->ResolveSystemIdtf("sc_node"))
        {
            continue;
        }

        bool hasOutgoingEdges = false;
        bool hasIncomingEdges = false;

        // Проверка исходящих рёбер
        ScIterator3Ptr outgoingEdgeIter = m_ctx->Iterator3(
            candidateNode,
            ScType::ConstPermPosArc,
            ScType::ConstNode
        );
        if (outgoingEdgeIter->Next())
        {
            hasOutgoingEdges = true;
        }

        // Проверка входящих рёбер
        ScIterator3Ptr incomingEdgeIter = m_ctx->Iterator3(
            ScType::ConstNode,
            ScType::ConstPermPosArc,
            candidateNode
        );
        if (incomingEdgeIter->Next())
        {
            hasIncomingEdges = true;
        }

        // Если тупик (нет исходящих рёбер)
        if (!hasOutgoingEdges)
        {
            structure.Append(candidateNode);

            ScAddr deadendEdge = m_ctx->CreateEdge(
                ScType::ConstPermPosArc,
                deadendVertexClass,
                candidateNode
            );
            if (deadendEdge.IsValid())
            {
                structure.Append(deadendEdge);
                structure.Append(deadendVertexClass);
            }
        }

        // Если антитупик (нет входящих рёбер)
        if (!hasIncomingEdges)
        {
            structure.Append(candidateNode);

            ScAddr antideadendEdge = m_ctx->CreateEdge(
                ScType::ConstPermPosArc,
                antideadendVertexClass,
                candidateNode
            );
            if (antideadendEdge.IsValid())
            {
                structure.Append(antideadendEdge);
                structure.Append(antideadendVertexClass);
            }
        }
    }
}