from graphviz import Digraph
from pprint import pprint

def get_user_input():
    Q = input("Enter NFA states (comma-separated): ").split(',')
    q0 = input("Enter initial state: ")
    alphabet = input("Enter alphabet symbols (comma-separated): ").split(',')
    has_epsilon = input("Does the NFA have epsilon transitions? (yes/no): ").lower() == 'yes'
    
    delta = []
    print("Enter transitions (enter 'done' to finish): ")
    while True:
        transition = input("Enter transition (e.g., A,0,B or A,ε,B): ")
        if transition.lower() == 'done':
            break
        delta.append(transition.split(','))

    F = input("Enter final states (comma-separated): ").split(',')

    return Q, q0, alphabet, delta, F, has_epsilon

def stringify(state):
    return '{' + ','.join(state) + '}'

def epsilon_closure(state, delta_dict):
    closure = set()
    stack = [state]

    while stack:
        current_state = stack.pop()
        closure.add(current_state)
        if 'ε' in delta_dict[current_state]:
            for next_state in delta_dict[current_state]['ε']:
                if next_state not in closure:
                    stack.append(next_state)
    return list(closure)

def build_dfa(Q, q0, alphabet, delta_dict, F, has_epsilon):
    dot = Digraph()
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'circle'

    dfa_states = []
    dfa_delta = []
    new_dfa_states = []

    q0_closure = epsilon_closure(q0, delta_dict)
    dfa_states.append(q0_closure)
    new_dfa_states.append(q0_closure)

    while new_dfa_states: 
        current_state = new_dfa_states.pop(0)

        for symbol in alphabet:
            next_states = []
            for nfa_state in current_state:
                if symbol in delta_dict[nfa_state]:
                    next_states.extend(delta_dict[nfa_state][symbol])

            next_states_closure = []
            for state in next_states:
                next_states_closure.extend(epsilon_closure(state, delta_dict))

            next_states_closure = sorted(set(next_states_closure))
            dfa_delta.append([current_state, symbol, next_states_closure])

            if next_states_closure not in dfa_states:
                dfa_states.append(next_states_closure)
                new_dfa_states.append(next_states_closure)

    for state in dfa_states:
        name = stringify(state)
        dot.node(name, name)

    for transition in dfa_delta:
        x, s, y = transition
        nameX = stringify(x)
        nameY = stringify(y)
        dot.edge(nameX, nameY, label=s)

    dot.node('BEGIN', '', shape='none')
    dot.edge('BEGIN', stringify(epsilon_closure(q0, delta_dict)), label='start')

    for dfa_state in dfa_states:
        for final_state in F:
            if final_state in dfa_state:
                name = stringify(dfa_state)
                dot.node(name, name, shape='doublecircle')

    dot.render(filename='gv_dfa.gv', view=True)

def test_dfa(dfa_states, delta_dict, q0, F):
    while True:
        input_str = input("Enter a string to test (type 'exit' to stop): ")
        if input_str.lower() == 'exit':
            break

        q = epsilon_closure(q0, delta_dict)
        for symbol in input_str:
            next_states = []
            for nfa_state in q:
                if symbol in delta_dict[nfa_state]:
                    next_states.extend(delta_dict[nfa_state][symbol])

            next_states_closure = []
            for state in next_states:
                next_states_closure.extend(epsilon_closure(state, delta_dict))

            if not next_states_closure:
                print(f"No transition for symbol '{symbol}' in current state(s) {q}.")
                break

            q = sorted(list(set(next_states_closure)))

        accepted = any(set(q) & set(F))
        if accepted:
            print("Accepted!")
        else:
            print("Not accepted.")

if __name__ == "__main__":
    Q, q0, alphabet, delta, F, has_epsilon = get_user_input()

    # Preprocessing of input
    delta_dict = {}
    for state in Q:
        delta_dict[state] = {}
        for symbol in alphabet:
            delta_dict[state][symbol] = []

    for transition in delta:
        x, s, y = transition  # Extract x, s, and y from the transition tuple
        if s != 'ε':
            delta_dict[x][s].extend(y.split(','))

    pprint(delta_dict)
    print()

    build_dfa(Q, q0, alphabet, delta_dict, F, has_epsilon)

    # Testing
    test_dfa(Q, delta_dict, q0, F)
