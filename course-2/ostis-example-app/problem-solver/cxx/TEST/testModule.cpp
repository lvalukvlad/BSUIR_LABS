/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "testModule.hpp"
#include "keynodes/keynodes.hpp"
#include "agents/testAgent.hpp"

using namespace testMod;

SC_IMPLEMENT_MODULE(test)

sc_result test::InitializeImpl()
{
  if (!testMod::Keynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(testAgent)

  return SC_RESULT_OK;
}

sc_result test::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(testAgent)

  return SC_RESULT_OK;
}
