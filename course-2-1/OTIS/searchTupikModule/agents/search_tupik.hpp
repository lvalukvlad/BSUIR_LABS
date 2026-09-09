#pragma once

#include "keynodes/search_tupik_keynodes.hpp"
#include <sc-memory/sc_agent.hpp>

class SearchTupikGraphAgent: public ScActionInitiatedAgent
{
public:
    ScAddr GetActionClass() const override;

    ScResult DoProgram(ScAction & action) override;
};