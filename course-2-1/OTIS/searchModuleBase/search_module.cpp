#include "search_module.hpp"
#include "agents/search_deadlocks_agent.hpp"
#include "keynodes/search_keynodes.hpp"

SC_IMPLEMENT_MODULE(DeadendFinderModule)

sc_result DeadendFinderModule::InitializeImpl()
{
    ScMemoryContext ctx(sc_access_lvl_make_min, "DeadendFinderModule");

    DeadendKeynodes::Init(&ctx); // Инициализация ключевых узлов

    // Регистрация агента
    SC_AGENT_REGISTER(DeadendAgent);

    return SC_RESULT_OK;
}

sc_result DeadendFinderModule::ShutdownImpl()
{
    SC_AGENT_UNREGISTER(DeadendAgent);

    return SC_RESULT_OK;
}