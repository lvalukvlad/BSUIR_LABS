#pragma once

#include <sc-memory/sc_module.hpp>
#include "agents/sc_class.hpp" // Добавлено локальное включение

class DeadendFinderModule : public ScModule
{
    SC_CLASS(DeadendFinderModule)
    SC_GENERATED_BODY()

public:
    sc_result InitializeImpl() override;
    sc_result ShutdownImpl() override;
};