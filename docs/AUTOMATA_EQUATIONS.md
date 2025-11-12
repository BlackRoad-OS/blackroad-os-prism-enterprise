# Automata Theory: Mathematical Foundations

## 1. Finite State Automaton (FSA) Definition

A finite automaton is formally defined as a 5-tuple:

$$M = (Q, \Sigma, \delta, q_0, F)$$

where:

- $Q$ — finite set of **states**
- $\Sigma$ — finite **alphabet** of input symbols
- $\delta: Q \times \Sigma \to Q$ — **transition function**
- $q_0 \in Q$ — **initial state**
- $F \subseteq Q$ — set of **accepting/final states**

## 2. State Transition Equations

Let:

- $x_n$ be the input at step $n$
- $z_n$ be the current state
- $z_{n+1}$ be the next state
- $w_n$ be the output at step $n$

Then the state update and output equations become:

- **State update:**

  $$z_{n+1} = \delta(z_n, x_n)$$

- **Output (Mealy machine):**

  $$w_n = \lambda(z_n, x_n)$$

- **Output (Moore machine):**

  $$w_n = \lambda(z_n)$$

## 3. Automata Variants

### Deterministic Finite Automaton (DFA)

A DFA requires that each state has exactly one transition for every symbol in the alphabet:

$$\forall q \in Q, \forall a \in \Sigma: \delta(q, a) \text{ is uniquely defined}$$

The extended transition function $\delta^*: Q \times \Sigma^* \to Q$ is defined recursively by:

- $\delta^*(q, \epsilon) = q$
- $\delta^*(q, wa) = \delta(\delta^*(q, w), a)$

### Nondeterministic Finite Automaton (NFA)

An NFA allows multiple transitions, so the transition function returns subsets of states:

$$\delta: Q \times \Sigma \to \mathcal{P}(Q)$$

### $\epsilon$-NFA

An $\epsilon$-NFA supports spontaneous transitions without consuming input symbols:

$$\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$$

## 4. Acceptance Condition

A string $w$ is accepted by automaton $M$ if the extended transition function lands in an accepting state:

$$\delta^*(q_0, w) \in F$$

The language recognized by $M$ is therefore:

$$L(M) = \{ w \in \Sigma^* \mid \delta^*(q_0, w) \in F \}$$

## 5. State Space Equations (Linear Systems View)

Some automata-inspired systems can be represented with linear state space equations:

- **State update:**

  $$\mathbf{z}_{n+1} = A \mathbf{z}_n + B \mathbf{x}_n$$

- **Output:**

  $$\mathbf{w}_n = C \mathbf{z}_n + D \mathbf{x}_n$$

where $A, B, C,$ and $D$ are matrices and $\mathbf{z}, \mathbf{x}, \mathbf{w}$ are vectors of compatible sizes.

## 6. Feedback and Equilibrium in Automata

In automata theory, feedback can be interpreted as routing the output of an automaton (such as a Mealy machine) back as part of its input, creating a closed-loop system. This mirrors classical feedback systems while remaining grounded in state transitions and output functions.

Consider a Mealy machine where the output at step $n$, $w_n = y(z_n, x_n)$, is fed back as an input for the next step, i.e., $x_{n+1} = f(w_n)$. The state update then becomes:

$$z_{n+1} = \delta(z_n, x_{n+1}) = \delta(z_n, f(w_n))$$

An equilibrium (or fixed point) occurs when the state and input/output values stop changing, i.e., $z_{n+1} = z_n$ and $x_{n+1} = x_n$. This happens when the feedback loop stabilizes, so that $w = y(z, x)$ and $x = f(w)$ yield consistent values.

For example, if $f$ is the identity and $y$ is a linear function, equilibrium is reached when $x = y(z, x)$, analogous to the condition $y \cdot x = y(x)$ in linear systems. In automata, such equilibria correspond to stable cycles or fixed points in the state transition graph.

## 7. Composition Patterns

- **Series composition:** the output of $M_1$ becomes the input to $M_2$.

  $$M = M_2 \circ M_1, \quad w = M_2(M_1(x))$$

- **Parallel composition:** both automata read the same input in lockstep.

  $$Q = Q_1 \times Q_2, \quad \delta((q_1, q_2), a) = (\delta_1(q_1, a), \delta_2(q_2, a))$$

## 8. Regular Languages and Kleene's Theorem

Kleene's theorem states that the following are equivalent characterizations of regular languages:

1. Languages recognized by DFAs.
2. Languages recognized by NFAs.
3. Languages described by regular expressions built from union $(\cup)$, concatenation, and Kleene star $(^*)$.

## 9. State Minimization and Myhill–Nerode

The Myhill–Nerode equivalence relation partitions $\Sigma^*$ by future behavior:

$$x \sim_L y \iff \forall z \in \Sigma^*: xz \in L \Leftrightarrow yz \in L$$

A minimal DFA for $L$ has one state per equivalence class and is unique up to isomorphism.

## 10. Pushdown Automata

A pushdown automaton (PDA) augments finite control with a stack:

$$M = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$$

$$\delta: Q \times (\Sigma \cup \{\epsilon\}) \times \Gamma \to \mathcal{P}(Q \times \Gamma^*)$$

A transition $ (q', \gamma) \in \delta(q, a, Z)$ indicates that on input $a$ with top-of-stack $Z$, the machine moves to state $q'$ and replaces $Z$ with the string $\gamma$.

## 11. Turing Machines

A Turing machine extends memory to an infinite tape:

$$M = (Q, \Sigma, \Gamma, \delta, q_0, q_{\text{accept}}, q_{\text{reject}})$$

with transition function

$$\delta: Q \times \Gamma \to Q \times \Gamma \times \{L, R\}$$

allowing the head to read/write tape symbols and move left or right each step.

## 12. Worked Example: Binary Counter Modulo 3

States track the remainder when reading a binary number modulo 3:

- $Q = \{0, 1, 2\}$
- $\Sigma = \{0, 1\}$
- $F = \{0\}$
- $\delta(q, a) = (2q + a) \bmod 3$

| Current state | Input | Next state |
| ------------- | ----- | ---------- |
| 0             | 0     | 0          |
| 0             | 1     | 1          |
| 1             | 0     | 2          |
| 1             | 1     | 0          |
| 2             | 0     | 1          |
| 2             | 1     | 2          |

The automaton accepts binary strings divisible by 3 when interpreted in big-endian order if state 0 is marked as accepting.
