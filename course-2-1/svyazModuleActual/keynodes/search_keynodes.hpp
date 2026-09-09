/*
 * This source file is part of an OSTIS project. For the latest info, see
 * http://ostis.net Distributed under the MIT License (See accompanying file
 * COPYING.MIT or copy at http://opensource.org/licenses/MIT)
 */

#pragma once

#include <sc-memory/sc_keynodes.hpp>

class SearchKeynodes : public ScKeynodes
{
public:
  static inline ScKeynode const action_search_component{"action_search_component", ScType::NodeConstClass};
};
