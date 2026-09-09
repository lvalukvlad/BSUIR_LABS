#pragma once

#include <sc-memory/sc_keynodes.hpp>
#include <string>

class DeadendKeynodes : public ScKeynodes
{
public:
    static ScAddr action_find_deadends;
    static ScAddr concept_deadend_vertex;
    static ScAddr concept_antideadend_vertex;

    // Метод инициализации ключевых узлов
    static void Init(ScMemoryContext * context);
};