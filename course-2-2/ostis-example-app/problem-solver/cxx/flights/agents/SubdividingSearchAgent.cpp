/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include <sc-agents-common/utils/GenerationUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>
#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/keynodes/coreKeynodes.hpp>

#include "SubdividingSearchAgent.hpp"

using namespace std;
using namespace utils;

namespace flightsMod
{

SC_AGENT_IMPLEMENTATION(setAgent)
{
  if (!edgeAddr.isValid())
    return SC_RESULT_ERROR;

  return SC_RESULT_OK;
}
}
