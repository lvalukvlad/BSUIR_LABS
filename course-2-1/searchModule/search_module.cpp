#include "search_module.hpp"
#include "agents/search_deadlocks_agent.hpp"

SC_IMPLEMENT_MODULE(SearchModule)

sc_result SearchModule::InitializeImpl()
{
    ScMemoryContext ctx(sc_access_lvl_make_min, "SearchModule");

    SearchKeynodes::Init(&ctx); // Инициализация ключевых узлов

    // Регистрация агента
    SC_AGENT_REGISTER(SearchDeadlocksAgent);

    return SC_RESULT_OK;
}

sc_result SearchModule::ShutdownImpl()
{
    SC_AGENT_UNREGISTER(SearchDeadlocksAgent);

    return SC_RESULT_OK;
}