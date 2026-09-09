#pragma once

#include <sc-memory/sc_agent.hpp>
#include <sc-memory/sc_event.hpp>
// #include <sc-memory/sc_class.hpp> // Удалено
#include "agents/sc_class.hpp" // Добавлено локальное включение
#include "keynodes/search_keynodes.hpp"

class DeadendAgent : public ScAgent
{
    SC_CLASS(DeadendAgent)
    SC_GENERATED_BODY()

public:
    ScAddr GetActionClass() const override;
    ScResult Run(ScAddr const & addr, ScAddr const & edgeAddr) override;

private:
    void FindDeadendsAndAntideadends(const ScAddr & graphNode, ScStructure & structure);
};