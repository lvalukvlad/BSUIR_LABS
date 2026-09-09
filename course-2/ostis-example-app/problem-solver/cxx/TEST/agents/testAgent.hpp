#pragma once

#include <sc-memory/kpm/sc_agent.hpp>

#include "keynodes/keynodes.hpp"
#include "testAgent.generated.hpp"

namespace testMod
{
class testAgent : public ScAgent
{
  SC_CLASS(Agent, Event(Keynodes::action_test, ScEvent::Type::AddOutputEdge))
  SC_GENERATED_BODY()
};

}  // namespace exampleModule
