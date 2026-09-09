#include "search_deadends_antideadends_agent.hpp"

#include "keynodes/search_keynodes.hpp"
#include <vector>
using namespace std;

void SearchDeadendsAntideadendsAgent::FindDeadendsAndAntideadends(ScAddr const & graphNode, ScStructure & structure) {
    // Узлы классов "Deadend_vertex" и "Antideadend_vertex"
    ScAddr deadendVertexClass = m_context.HelperResolveSystemIdtf("concept_deadend_vertex");
    ScAddr antideadendVertexClass = m_context.HelperResolveSystemIdtf("concept_antideadend_vertex");

    if (!deadendVertexClass.IsValid() || !antideadendVertexClass.IsValid()) {
        return; 
    }

    // Итерация по вершинам графа
    ScIterator3Ptr vertexIter = m_context.CreateIterator3(
        graphNode,
        ScType::EdgeAccessConstPosPerm,
        ScType::NodeConst
    );

    while (vertexIter->Next()) {
        ScAddr candidateNode = vertexIter->Get(2);
        if (candidateNode == m_context.HelperResolveSystemIdtf("sc_node")) {
            continue; 
        }

        bool hasOutgoingEdges = false;
        bool hasIncomingEdges = false;

        // Проверка исходящих рёбер
        ScIterator3Ptr outgoingEdgeIter = m_context.CreateIterator3(
            candidateNode,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst
        );
        if (outgoingEdgeIter->Next()) {
            hasOutgoingEdges = true;
        }

        // Проверка входящих рёбер
        ScIterator3Ptr incomingEdgeIter = m_context.CreateIterator3(
            ScType::NodeConst,
            ScType::EdgeAccessConstPosPerm,
            candidateNode
        );
        if (incomingEdgeIter->Next()) {
            hasIncomingEdges = true;
        }

        // Если тупик (нет исходящих рёбер)
        if (!hasOutgoingEdges) {
            structure.Append(candidateNode);

            ScAddr deadendEdge = m_context.CreateEdge(
                ScType::EdgeAccessConstPosPerm,
                deadendVertexClass,
                candidateNode
            );
            if (deadendEdge.IsValid()) {
                structure.Append(deadendEdge);
                structure.Append(deadendVertexClass);
            }
        }

        // Если антитупик (нет входящих рёбер)
        if (!hasIncomingEdges) {
            structure.Append(candidateNode);

            ScAddr antideadendEdge = m_context.CreateEdge(
                ScType::EdgeAccessConstPosPerm,
                antideadendVertexClass,
                candidateNode
            );
            if (antideadendEdge.IsValid()) {
                structure.Append(antideadendEdge);
                structure.Append(antideadendVertexClass);
            }
        }
    }
}

ScAddr SearchDeadendsAntideadendsAgent::GetActionClass() const {
    return SearchKeynodes::action_search_deadends_antideadends;
}

ScResult SearchDeadendsAntideadendsAgent::DoProgram(ScAction & action) {
    auto const & [SetAddr] = action.GetArguments<1>();

    // Проверка переданного графа
    if (!m_context.IsElement(SetAddr)) {
        return action.FinishWithError();
    }

    // Структура для результата
    ScStructure structure = m_context.GenerateStructure();

    FindDeadendsAndAntideadends(SetAddr, structure);

    // Проверка на пустую структуру
    if (structure.IsEmpty()) {
        return action.FinishUnsuccessfully(); // Завершаем, если вершин нет
    }

    // Результат
    action.SetResult(structure);

    return action.FinishSuccessfully();
}
