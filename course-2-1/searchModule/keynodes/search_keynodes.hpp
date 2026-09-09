#pragma once

#include <sc-memory/sc_keynodes.hpp>

class SearchKeynodes : public ScKeynodes
{
public:
    static inline ScKeynode const action_search_deadlocks{"action_search_deadlocks", ScType::ConstNodeClass};
    static inline ScKeynode const deadlock{"deadlock", ScType::ConstNodeClass};
    static inline ScKeynode const anti_deadlock{"anti_deadlock", ScType::ConstNodeClass};
};