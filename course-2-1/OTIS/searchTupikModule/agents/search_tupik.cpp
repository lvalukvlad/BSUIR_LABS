#include "search_tupik.hpp"
#include "keynodes/search_tupik_keynodes.hpp"
#include <string>

using namespace std;

ScAddr SearchTupikGraphAgent::GetActionClass() const
{
    return OkrKeynodes::action_find_tupik_graph;
}

ScResult SearchTupikGraphAgent::DoProgram(ScAction &action)
{
    auto const &[argAddr] = action.GetArguments<1>();

    if (!m_context.IsElement(argAddr))
    {
        SC_AGENT_LOG_ERROR("Set is not specified");
        return action.FinishWithError();
    }


    ScStructure structure = m_context.GenerateStructure();

    vector<ScAddr> tupiki;
    vector<ScAddr> antitupiki;

    ScIterator3Ptr const it3 = m_context.CreateIterator3(
        argAddr,
        ScType::EdgeAccessConstPosPerm,
        ScType::NodeConst);


    
    ScAddr nrel_tupiki;
    ScAddr nrel_anti_tupiki;

    ScAddr tuple1 = m_context.CreateNode(ScType::NodeConstTuple);
    ScAddr tuple2 = m_context.CreateNode(ScType::NodeConstTuple);

    m_context.SearchElementBySystemIdentifier("nrel_tupkiki_vershiny", nrel_tupiki);
    m_context.SearchElementBySystemIdentifier("nrel_antitupkiki_vershiny", nrel_anti_tupiki);
    ScAddr const &connector1 = m_context.GenerateConnector(ScType::EdgeDCommonConst, argAddr, tuple1);
    ScAddr const &connector2 = m_context.GenerateConnector(ScType::EdgeDCommonConst, argAddr, tuple2);
    ScAddr const &connector_1 = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, nrel_tupiki, connector1);
    ScAddr const &connector_2 = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, nrel_anti_tupiki, connector2);

    
    SC_AGENT_LOG_ERROR("FFFFFFFFFFFFFFFFFFFFFf");

    while (it3->Next())
    {
        if (m_context.GetElementType(it3->Get(2)) == ScType::NodeConstClass)
            continue;
        if (m_context.GetElementType(it3->Get(2)) == ScType::NodeLink)
            continue;

        ScAddr vershina = it3->Get(2);
        ScTemplate templ1;
        templ1.Triple(
            vershina,
            ScType::VarCommonArc,
            ScType::NodeVar);

        ScTemplate templ2;
        templ2.Triple(
            ScType::NodeVar,
            ScType::VarCommonArc,
            vershina);

        ScTemplateSearchResult result1;
        bool const isFoundByTemplate1 = m_context.SearchByTemplate(templ1, result1);

        ScTemplateSearchResult result2;
        bool const isFoundByTemplate2 = m_context.SearchByTemplate(templ2, result2);

        if (isFoundByTemplate1 && !isFoundByTemplate2)
        {
            tupiki.push_back(vershina);
            ScAddr const &connector = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, tuple1, vershina);
            structure << vershina << connector;
        }
        else if (!isFoundByTemplate1 && isFoundByTemplate2 || isFoundByTemplate1 && isFoundByTemplate2)
        {
            antitupiki.push_back(vershina);
            ScAddr const &connector = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, tuple2, vershina);
            structure << vershina << connector;
        }
    }

    if(tupiki.empty()){
        ScAddr empty; 
        m_context.SearchElementBySystemIdentifier("empty_set", empty);
        ScAddr const &connector_0 = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, empty, tuple1);
        structure << empty<< connector_0;
    }
    else if(antitupiki.empty()){
        ScAddr empty; 
        m_context.SearchElementBySystemIdentifier("empty_set", empty);
        ScAddr const &connector_0 = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, empty, tuple2);
        structure << empty<< connector_0;
    }


    structure << nrel_tupiki << nrel_anti_tupiki << connector1<< connector2 << connector_2<< connector_1 << argAddr << tuple1<< tuple2;

    action.SetResult(structure);
    return action.FinishSuccessfully();
}