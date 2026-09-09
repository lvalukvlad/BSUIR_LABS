#include <iostream>

#include <sc-memory/sc_memory.hpp>
#include <sc-memory/sc_stream.hpp>
#include <sc-memory/sc_template_search.cpp>

#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>

#include "testAgent.hpp"

using namespace std;
using namespace utils;

namespace testMod
{
SC_AGENT_IMPLEMENTATION(testAgent)
{
  SC_LOG_DEBUG("testAgent: started");
  ScAddr actionNode = otherAddr;

  SC_LOG_INFO("My agent is starting");

  return SC_RESULT_OK;
}



}  // namespace exampleModule
