#include "search_keynodes.hpp"
#include <sc-memory/sc_memory.hpp>

ScAddr DeadendKeynodes::action_find_deadends;
ScAddr DeadendKeynodes::concept_deadend_vertex;
ScAddr DeadendKeynodes::concept_antideadend_vertex;

void DeadendKeynodes::Init(ScMemoryContext * context)
{
    action_find_deadends = context->ResolveElementSystemIdentifier("action_find_deadends");
    concept_deadend_vertex = context->ResolveElementSystemIdentifier("concept_deadend_vertex");
    concept_antideadend_vertex = context->ResolveElementSystemIdentifier("concept_antideadend_vertex");
}