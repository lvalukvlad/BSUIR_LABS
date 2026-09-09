#pragma once

#include <sc-memory/sc_keynodes.hpp>

class OkrKeynodes:public ScKeynodes
{
public:
    static inline ScKeynode const action_find_tupik_graph{"action_find_tupik_graph", ScType::NodeConstClass};
};