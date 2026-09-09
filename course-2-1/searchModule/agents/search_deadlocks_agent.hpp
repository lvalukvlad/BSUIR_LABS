#pragma once

#include <sc-memory/sc_memory.hpp>
#include <sc-memory/sc_agent.hpp>
#include <vector>
#include "keynodes/search_keynodes.hpp"

class SearchDeadlocksAgent : public ScAgent
{
    SC_CLASS(Agent, Event(SearchKeynodes::action_search_deadlocks, ScEvent::Type::AddOutputEdge))
    SC_GENERATED_BODY()

public:
    ScAddr GetActionClass() const override;
    ScResult Run(ScAddr const & addr, ScAddr const & edgeAddr) override;

private:
    bool IsDeadlock(const ScAddr &node);
    bool IsAntiDeadlock(const ScAddr &node);
};