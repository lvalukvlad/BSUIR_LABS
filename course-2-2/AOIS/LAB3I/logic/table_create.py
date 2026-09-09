from logic.to_bin import to_bin
from logic.make_operation import make_operation

def rpn_check(rpn):
    vars: [str] = []
    for element in range(len(rpn)):
        if rpn[element] == 0 or rpn[element] == 1:
            vars.append(rpn[element])
            continue
        if rpn[element] == '!':
            if vars[-1] == 0:
                vars[-1] = 1
            else:
                vars[-1] = 0
        else:
            el: int = make_operation(vars[-2], vars[-1], rpn[element])
            vars.pop()
            vars.pop()
            vars.append(el)
    return vars[0]

def table_create(exp: str, rpn: list, vars: list):
    vars_in_degree: int = 2 ** len(vars)
    vars_string: str = ''
    for i in vars:
        vars_string += i + ' '
    vars_string += '' + exp
    print(vars_string)
    index_form: list = []
    pdnf_exp_list: str = ''
    pcnf_exp_list: str = ''
    pdnf_list: list = []
    pcnf_list: list = []
    for i in range(vars_in_degree):
        bool_vars = to_bin(i, len(vars))
        str_numbers = [str(n) for n in bool_vars]
        bool_rpn: list = rpn.copy()
        for f in range(len(vars)):
            indices = [index for index, val in enumerate(bool_rpn) if val == vars[f]]
            for index in indices:
                if '!' in vars[f]:
                    bool_rpn[index] = 1 - bool_vars[f]
                else:
                    bool_rpn[index] = bool_vars[f]
        check_info = rpn_check(bool_rpn)
        index_form.append(str(check_info))
        bool_vars_string = ' '.join(str_numbers) + '  ' + str(check_info)
        result_exp = ''
        if check_info == 1:
            for f in range(len(vars)):
                if bool_vars[f] == 1:
                    result_exp += vars[f].replace('!', '')
                else:
                    result_exp += '!' + vars[f].replace('!', '')
                if check_info == 1 and f + 1 != len(vars):
                    result_exp += '&'
            pdnf_list.append(str(i))
            pdnf_exp_list += '(' + result_exp + ')|'
        else:
            for f in range(len(vars)):
                if bool_vars[f] == 1:
                    result_exp += '!' + vars[f].replace('!', '')
                else:
                    result_exp += vars[f].replace('!', '')
                if check_info == 0 and f + 1 != len(vars):
                    result_exp += '|'
            pcnf_list.append(str(i))
            pcnf_exp_list += '(' + result_exp + ')&'
        print(bool_vars_string)
    if len(pdnf_exp_list) != 0:
        pdnf_exp_list = pdnf_exp_list[:-1]
    if len(pcnf_exp_list) != 0:
        pcnf_exp_list = pcnf_exp_list[:-1]
    return {'index': ''.join(index_form), 'pdnf': '(' + ', '.join(pdnf_list) + ')&', 'pcnf': '(' + ', '.join(pcnf_list) + ')|', 'pdnf_exp_list': pdnf_exp_list,
            'pcnf_exp_list': pcnf_exp_list}