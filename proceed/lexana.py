r'lexana means lexical analysis'

from io import TextIOWrapper
from queue import Queue


class NFA:

    def __init__(self, rulelist: map, startstate: str, acceptstate: str, epsilon: str) -> None:
        self.transtable = {}
        self.start_state = startstate
        self.accept_state = acceptstate
        self.epsilon = epsilon
        self.alphabet = set()
        self.states = set()
        self.build(rulelist)
        # print("alphabet:{}".format(self.alphabet))
        # print("transtable:{}".format(self.transtable))

    def build(self, rulelist: map):
        for i in rulelist:
            self.transtable[i] = {}
            m = self.transtable[i]
            for j in rulelist[i]:
                if len(j) > 2 and (j[0] == '<' or j[0] == '>') and j[1] == '<':
                    ne, e = j[0], j[1:]
                    self.alphabet.add(ne)
                    self.states.add(e)
                    if ne not in self.transtable[i]:
                        m[ne] = [e]
                    else:
                        m[ne].append(e)
                else:
                    if '<' not in j or j == '<':
                        self.alphabet.add(j)
                        if j not in m.keys():
                            m[j] = [self.accept_state]
                        else:
                            m[j].append(self.accept_state)
                    elif j[0] == '<':
                        self.states.add(j)
                        if self.epsilon not in self.transtable[i]:
                            m[self.epsilon] = [j]
                        else:
                            m[self.epsilon].append(j)
                    else:
                        ne, e = j.split(sep='<')
                        self.alphabet.add(ne)
                        self.states.add('<' + e)
                        if ne not in self.transtable[i]:
                            m[ne] = ['<' + e]
                        else:
                            m[ne].append('<' + e)
        self.states.add(self.start_state)
        self.states.add(self.accept_state)
        if self.epsilon not in self.alphabet:
            self.alphabet.add(self.epsilon)


class DFA():

    def __init__(self, nfa: NFA) -> None:
        self.name = nfa.start_state
        self.epsilon = nfa.epsilon
        self.nfa_states = nfa.states
        self.nfa_transtable = nfa.transtable
        self.nfa_start_state = nfa.start_state
        self.nfa_accept_state = nfa.accept_state
        self.alphabet = nfa.alphabet
        self.transtable = {}
        self.states = set()
        self.nfa2dfa()
        self.minimize()

    def nfa2dfa(self):
        self.transtable = {}
        self.start_state = frozenset(self.closure([self.nfa_start_state]))
        self.states.add(self.start_state)
        q = Queue()
        q.put(self.start_state)
        while not q.empty():
            s1 = q.get()
            for a in self.alphabet:
                if a == self.epsilon:
                    continue
                nxt = frozenset(self.closure(
                    self.move(s=s1, ne=a, table=self.nfa_transtable)))
                if len(nxt) > 0:
                    if s1 not in self.transtable.keys():
                        self.transtable[s1] = {}
                    if a in self.transtable[s1]:
                        continue
                    self.transtable[s1][a] = nxt
                    q.put(nxt)
                    self.states.add(nxt)
        self.accept_state = set()
        for ss in self.states:
            if self.nfa_accept_state in ss:
                self.accept_state.add(ss)
        # print("states:{}".format(self.states))
        # print("accept states:{}".format(self.accept_state))
        # print("transtable:{}".format(self.transtable))

    def move(self, s: list, ne: str, table: map) -> list:
        m = []
        for i in s:
            if i not in table.keys():
                continue
            if ne in table[i].keys():
                x = table[i][ne]
                for j in x:
                    m.append(j)
        return m

    def closure(self, s: list) -> set:
        q = Queue()
        cnt = set()
        for i in s:
            q.put(i)
            cnt.add(i)
        while not q.empty():
            t = q.get()
            if t not in self.nfa_transtable.keys():
                continue
            if self.epsilon in self.nfa_transtable[t].keys():
                for i in self.nfa_transtable[t][self.epsilon]:
                    if i in cnt:
                        continue
                    q.put(i)
                    cnt.add(i)
        return cnt

    def minimize(self) -> None:
        partition = [frozenset(self.accept_state), frozenset(
            self.states-self.accept_state)]
        trans_full = {}
        for s in self.states:
            # print(s)
            if s not in self.transtable:
                self.transtable[s] = {}
            trans_full[s] = {}
            for a in self.alphabet:
                # print(a)
                if a in self.transtable[s]:
                    trans_full[s][a] = self.transtable[s][a]
                else:
                    trans_full[s][a] = frozenset({'null'})
        while True:
            # print("partition:{}".format(partition))
            new_partition = []
            for g in partition:
                if len(g) < 2:
                    new_partition.append(g)
                    # print('new_partition:{}'.format(new_partition))
                    continue
                new_groups = {}
                for i, s in enumerate(g):
                    # print(i, s)
                    ts = self.movetuple(s, trans_full, partition)
                    if ts in new_groups:
                        new_groups[ts].add(s)
                    else:
                        new_groups[ts] = {0}
                        new_groups[ts].add(s)
                        new_groups[ts].remove(0)
                # print("new_groups:{}".format(new_groups))
                for i in new_groups.values():
                    new_partition.append(frozenset(i))
                # new_partition.extend(new_groups.values())
                # print('new_partition:{}'.format(new_partition))
            if new_partition == partition:
                break
            partition = new_partition
        t_trasnstable, t_states, t_ststates, t_accstates = {}, set(
            partition), set(), set()
        for i in t_states:
            for j in i:
                for a in self.transtable[j]:
                    for s in t_states:
                        if self.transtable[j][a] in s:
                            if i not in t_trasnstable:
                                t_trasnstable[i] = {}
                            t_trasnstable[i][a] = s
                            break
            for s in self.accept_state:
                if s in i:
                    t_accstates.add(s)
            if self.start_state in i:
                t_ststates = i
        # print("t_ststates:{}".format(t_ststates))
        # print("t_accstates:{}".format(t_accstates))
        # print("t_transtable:{}".format(t_trasnstable))
        self.accept_state = frozenset(t_accstates)
        self.start_state = t_ststates
        self.transtable = t_trasnstable

    def movetuple(self, state: frozenset, table: map, part: list) -> tuple:
        nxtuple = []
        for a in self.alphabet:
            ns = table[state][a]
            if ns == frozenset({'null'}):
                nxtuple.append(ns)
            else:
                for g in part:
                    if ns in g:
                        nxtuple.append(frozenset(g))
                        break
        return tuple(nxtuple)

    def run(self, s: str) -> bool:
        ss = self.start_state
        for c in s:
            if ss not in self.transtable:
                return False
            if c not in self.transtable[ss]:
                return False
            ss = self.transtable[ss][c]
        if ss == self.accept_state or ss.issubset(self.accept_state):
            return True
        print(ss, self.accept_state)
        return False


class LOADER:

    def __init__(self) -> None:
        pass

    def loadcodefile(self, filedir: str, dfalist: list, keywords: set, delimiter: str) -> list:
        ans, ret = [], []
        f = open(filedir, "r")
        lines = f.readlines()
        for i, line in enumerate(lines):
            tokens = line.split()
            for token in tokens:
                ans.append((i, token))
        DFAtable = {}
        for i in dfalist:
            DFAtable[i.name] = i
        for t in ans:
            idx, ctt = t
            length = len(ctt)
            left, right = 0, length
            while right > left:
                s_token = ctt[left:right]
                t_type = 'undefined'
                flag = False
                if s_token in keywords:
                    flag = True
                    t_type = 'keyword_'+s_token
                elif s_token == '=':
                    flag = True
                    t_type = 'operator_='
                else:
                    for dfa in dfalist:
                        if dfa.run(s_token):
                            flag = True
                            t_type = dfa.name[1:-1]
                            if t_type == delimiter:
                                t_type += '_'+s_token
                            break
                if flag:
                    ret.append((idx+1, t_type, s_token))
                    left = right
                    right = length
                else:
                    if right-1 == left:
                        print('ERROR: unexpected symbol \'{s_token}\' at row {idx}, column {left}, in {line}'.format(
                            idx=idx+1, s_token=s_token, left=left, line=lines[idx].strip()))
                    right -= 1
        return ret

    def loadlexicalfile(self, filedir: str):
        ans = []
        f = open(filedir, "r")
        line = f.readline()
        total = int(line.strip())
        # print('total:{}'.format(total))
        line = f.readline()
        delimiter = line.strip()
        cnt = 0
        line = f.readline()
        keywords = set(line.split())
        line = f.readline()
        while line and cnt < total:
            if line.isspace():
                line = f.readline()
                continue
            else:
                n = int(line.strip())
                # print('n:{}'.format(n))
                rule, ststate, endstate, epsl = self.loadgrammar(f, n)
                # print(rule, ststate, endstate, epsl)
                nxtDFA = DFA(NFA(rule, ststate, endstate, epsl))
                ans.append(nxtDFA)
                cnt += 1
                line = f.readline()
        f.close()
        return delimiter, keywords, ans

    def loadgrammar(self, fileHandler: TextIOWrapper, len: int):
        cnt = 0
        rule = {}
        line = fileHandler.readline()
        ststate, endstate, epsl, op_sep, op_or = line.split()
        if op_or == 'space':
            op_or = ' '
        line = fileHandler.readline()
        while line and cnt < len:
            if line.isspace():
                line = fileHandler.readline()
                continue
            else:
                cnt += 1
                line = line.strip()
                l, r = line.split(sep=op_sep)
                list_r = r.split(sep=op_or)
                rule[l] = list_r
                if cnt < len:
                    line = fileHandler.readline()
        return rule, ststate, endstate, epsl


class PARSER:
    def __init__(self, lexicalpath: str, codepath: str) -> None:
        self.lexpath = lexicalpath
        self.codepath = codepath

    def parse(self) -> list:
        l = LOADER()
        delimiter, keywords, DFAlist = l.loadlexicalfile(self.lexpath)
        tokenlist = l.loadcodefile(self.codepath, DFAlist, keywords, delimiter)
        errorlist = self.check(tokenlist)
        return tokenlist, errorlist

    def check(self, tokenlist: list) -> list:
        ans = []
        for t in tokenlist:
            if t[1] == 'const_integer':
                i = int(t[2])
                if i >= 2**32 or i < -2**32:
                    ans.append(
                        'WARNING: const integer out of range, for {0} in row {1}'.format(i, t[0]))
            if t[1] == 'const_float':
                if 'E' in t[2]:
                    l, r = t[2].split('E')
                    i = int(r)
                    if i > 100 or i < -100:
                        ans.append(
                            'WARNING: const float out of range, for {0} in row {1}'.format(i, t[0]))
        return ans
