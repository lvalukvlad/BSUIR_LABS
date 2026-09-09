/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "exampleModule.hpp"
#include "keynodes/keynodes.hpp"
#include "agents/SubdividingSearchAgent.hpp"
#include "agents/IsomorphicSearchAgent.hpp"

using namespace flightsMod;

SC_IMPLEMENT_MODULE(FlightsModule)

sc_result FlightsModule::InitializeImpl()
{
  if (!flightsMod::Keynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(flightsAgent)
  SC_AGENT_REGISTER(setAgent)

  return SC_RESULT_OK;
}

sc_result FlightsModule::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(flightsAgent)
  SC_AGENT_UNREGISTER(setAgent)

  return SC_RESULT_OK;
}
