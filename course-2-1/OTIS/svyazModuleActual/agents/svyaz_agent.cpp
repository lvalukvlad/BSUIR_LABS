/*
 * This source file is part of an OSTIS project. For the latest info, see
 * http://ostis.net Distributed under the MIT License (See accompanying file
 * COPYING.MIT or copy at http://opensource.org/licenses/MIT)
 */

#include "svyaz_agent.hpp"

#include "keynodes/search_keynodes.hpp"
#include <vector>
using namespace std;
/*
void SearchSvyazAgent::FindCycles(const ScAddr &currentAddr, 
                vector<ScAddr> &poseshen, 
                ScStructure &structure) {
    // Создаем итератор для поиска соседей
    ScIterator3Ptr it3_1 = m_context.CreateIterator3(
        currentAddr,
        ScType::EdgeDCommonConst,
        ScType::NodeConst
    );

    while (it3_1->Next()) {
        ScAddr neighborAddr = it3_1->Get(2);
        if (!m_context.IsElement(neighborAddr)) {
        SC_AGENT_LOG_ERROR("Invalid neighbor address");
        continue;
        }
        if (!poseshen.empty() && poseshen[0] == neighborAddr) {
            SC_AGENT_LOG_INFO("Цикл найден");
            for (const auto &addr : poseshen) {
                structure << addr; 
            }
            structure << neighborAddr; 
            continue; 
        }

        
        poseshen.push_back(neighborAddr);
        FindCycles(neighborAddr, poseshen, structure);
        poseshen.pop_back();
    }
}

ScAddr SearchSvyazAgent::GetActionClass() const
{
  return SearchKeynodes::action_search_component;
}

ScResult SearchSvyazAgent::DoProgram(ScAction & action)
{
  auto const & [SetAddr] = action.GetArguments<1>();
  if(!m_context.IsElement(SetAddr))
  {
    SC_AGENT_LOG_ERROR("Graph is not specified");
    return action.FinishWithError();
  }
ScStructure structure = m_context.GenerateStructure();
vector<ScAddr> poseshen;

ScIterator3Ptr const it3 = m_context.CreateIterator3(
SetAddr,
ScType::EdgeAccessConstPosPerm,
ScType::NodeConst
);
SC_AGENT_LOG_INFO("Agent - ok1");

while (it3->Next()) {
    SC_AGENT_LOG_INFO("Agent - ok2");
    ScAddr vershinaAddr = it3->Get(2);
    poseshen.clear();
    poseshen.push_back(vershinaAddr);
    FindCycles(vershinaAddr, poseshen, structure);
}

action.SetResult(structure);
return action.FinishSuccessfully();
}
*/
void SearchSvyazAgent::FindCycles(const ScAddr &startAddr, 
                                   ScStructure &structure) {
    stack<pair<ScAddr,vector<ScAddr>>> stack;
    vector<ScAddr> poseshen;
    poseshen.push_back(startAddr);
    stack.push({startAddr, poseshen});

    while (!stack.empty()) {
        auto [tekushAddr, tekushPoseshen] = stack.top();
        stack.pop();

        
        ScIterator3Ptr it3_1 = m_context.CreateIterator3(
            tekushAddr,
            ScType::EdgeDCommonConst,
            ScType::NodeConst
        );

        while (it3_1->Next()) {
            ScAddr sosediAddr = it3_1->Get(2);

            
            if (find(tekushPoseshen.begin(), tekushPoseshen.end(), sosediAddr) != tekushPoseshen.end()) {
                if (sosediAddr == startAddr) {
                    SC_AGENT_LOG_INFO("Цикл найден");
                    for (const auto &element : tekushPoseshen) {
                        structure << element;
                    }
                    structure << sosediAddr; 
                }
                continue;
            }

            vector<ScAddr> nextPoseshen = tekushPoseshen;
            nextPoseshen.push_back(sosediAddr);
            stack.push({sosediAddr, nextPoseshen});
        }
    }
}

ScAddr SearchSvyazAgent::GetActionClass() const {
    return SearchKeynodes::action_search_component;
}

ScResult SearchSvyazAgent::DoProgram(ScAction & action) {
    auto const & [SetAddr] = action.GetArguments<1>();
    if (!m_context.IsElement(SetAddr)) {
        SC_AGENT_LOG_ERROR("Graph is not specified");
        return action.FinishWithError();
    }

    ScStructure structure = m_context.GenerateStructure();
    ScIterator3Ptr const it3 = m_context.CreateIterator3(
        SetAddr,
        ScType::EdgeAccessConstPosPerm,
        ScType::NodeConst
    );
    SC_AGENT_LOG_INFO("Agent - ok1");

    while (it3->Next()) {
        SC_AGENT_LOG_INFO("Agent - ok2");
        ScAddr vershinaAddr = it3->Get(2);
        FindCycles(vershinaAddr, structure);
    }

    action.SetResult(structure);
    return action.FinishSuccessfully();
}