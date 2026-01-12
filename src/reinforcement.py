import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import random
from ui import section_header
import warnings
warnings.filterwarnings('ignore')

class SimpleGridWorld:
    """A simple grid world environment for RL demonstrations."""

    def __init__(self, size=5):
        self.size = size
        self.state = (0, 0)  # Start at top-left
        self.goal = (size-1, size-1)  # Goal at bottom-right
        self.actions = ['up', 'down', 'left', 'right']
        self.action_map = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

    def reset(self):
        self.state = (0, 0)
        return self.state

    def step(self, action):
        if action not in self.actions:
            raise ValueError(f"Invalid action: {action}")

        dx, dy = self.action_map[action]
        new_x = max(0, min(self.size-1, self.state[0] + dx))
        new_y = max(0, min(self.size-1, self.state[1] + dy))

        self.state = (new_x, new_y)

        # Reward structure
        if self.state == self.goal:
            reward = 10  # Goal reached
            done = True
        elif self.state[0] == 0 or self.state[0] == self.size-1 or self.state[1] == 0 or self.state[1] == self.size-1:
            reward = -0.1  # Penalty for hitting walls (though we prevent it)
            done = False
        else:
            reward = -0.01  # Small penalty for each step
            done = False

        return self.state, reward, done

    def get_state_space_size(self):
        return self.size * self.size

    def get_action_space_size(self):
        return len(self.actions)

class QLearningAgent:
    """Q-Learning agent implementation."""

    def __init__(self, state_space, action_space, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.state_space = state_space
        self.action_space = action_space
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = np.zeros((state_space, action_space))

    def get_action(self, state):
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_space)
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        """Update Q-table using Q-learning update rule."""
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error

    def get_policy(self):
        """Extract deterministic policy from Q-table."""
        return np.argmax(self.q_table, axis=1)

class PolicyGradientAgent:
    """Simple policy gradient agent using REINFORCE."""

    def __init__(self, state_space, action_space, alpha=0.01):
        self.state_space = state_space
        self.action_space = action_space
        self.alpha = alpha
        # Simple policy network (just weights for each state-action pair)
        self.policy_weights = np.random.randn(state_space, action_space) * 0.01

    def get_action_probs(self, state):
        """Get action probabilities for a state."""
        logits = self.policy_weights[state]
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    def get_action(self, state):
        """Sample action from policy."""
        probs = self.get_action_probs(state)
        return np.random.choice(self.action_space, p=probs)

    def update_policy(self, episode_states, episode_actions, episode_rewards, gamma=0.99):
        """Update policy using REINFORCE algorithm."""
        # Calculate discounted rewards
        discounted_rewards = []
        cumulative_reward = 0
        for reward in reversed(episode_rewards):
            cumulative_reward = reward + gamma * cumulative_reward
            discounted_rewards.insert(0, cumulative_reward)

        # Normalize rewards
        discounted_rewards = np.array(discounted_rewards)
        if len(discounted_rewards) > 1:
            discounted_rewards = (discounted_rewards - np.mean(discounted_rewards)) / (np.std(discounted_rewards) + 1e-8)

        # Update policy weights
        for state, action, reward in zip(episode_states, episode_actions, discounted_rewards):
            probs = self.get_action_probs(state)
            # Policy gradient update
            gradient = np.zeros_like(self.policy_weights[state])
            gradient[action] = 1 - probs[action]
            self.policy_weights[state] += self.alpha * reward * gradient

def show_reinforcement_learning(df):
    section_header("Reinforcement Learning", "Train agents using Q-Learning and Policy Gradients on custom environments.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # RL Method selection
    rl_method = st.selectbox("Select RL Algorithm",
                           ["Q-Learning", "Policy Gradients", "RL for Classification"],
                           key="rl_method")

    if rl_method in ["Q-Learning", "Policy Gradients"]:
        show_tabular_rl(rl_method)
    else:
        show_rl_classification(df)

def show_tabular_rl(method):
    """Demonstrate tabular RL on Grid World environment."""

    st.subheader(f"{method} on Grid World")

    # Environment setup
    env_size = st.slider("Grid World Size", 3, 8, 5, key="env_size")
    env = SimpleGridWorld(env_size)

    # Agent parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        episodes = st.slider("Training Episodes", 100, 2000, 500, key="episodes")
    with col2:
        alpha = st.slider("Learning Rate (α)", 0.01, 0.5, 0.1, key="alpha")
    with col3:
        gamma = st.slider("Discount Factor (γ)", 0.1, 0.99, 0.9, key="gamma")

    if method == "Q-Learning":
        epsilon = st.slider("Exploration Rate (ε)", 0.01, 0.3, 0.1, key="epsilon")
        agent = QLearningAgent(env.get_state_space_size(), env.get_action_space_size(),
                              alpha=alpha, gamma=gamma, epsilon=epsilon)
    else:  # Policy Gradients
        agent = PolicyGradientAgent(env.get_state_space_size(), env.get_action_space_size(),
                                   alpha=alpha)

    if st.button("Train RL Agent", key="train_rl"):
        with st.spinner("Training RL agent..."):
            rewards_history = []
            episode_lengths = []

            for episode in range(episodes):
                state = env.reset()
                state_idx = state[0] * env.size + state[1]
                episode_reward = 0
                episode_steps = 0
                episode_states = []
                episode_actions = []
                episode_rewards = []

                done = False
                while not done and episode_steps < 100:  # Max steps per episode
                    if method == "Q-Learning":
                        action_idx = agent.get_action(state_idx)
                    else:  # Policy Gradients
                        action_idx = agent.get_action(state_idx)

                    action = env.actions[action_idx]
                    next_state, reward, done = env.step(action)
                    next_state_idx = next_state[0] * env.size + next_state[1]

                    episode_reward += reward
                    episode_steps += 1

                    if method == "Q-Learning":
                        agent.update_q_table(state_idx, action_idx, reward, next_state_idx)
                    else:  # Policy Gradients
                        episode_states.append(state_idx)
                        episode_actions.append(action_idx)
                        episode_rewards.append(reward)

                    state = next_state
                    state_idx = next_state_idx

                # Update policy gradients at end of episode
                if method == "Policy Gradients":
                    agent.update_policy(episode_states, episode_actions, episode_rewards, gamma)

                rewards_history.append(episode_reward)
                episode_lengths.append(episode_steps)

        # Display results
        st.success("Training completed!")

        # Performance plots
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Learning Curve")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(rewards_history, alpha=0.7)
            ax.set_xlabel("Episode")
            ax.set_ylabel("Total Reward")
            ax.set_title(f"{method} Learning Curve")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

        with col2:
            st.subheader("Episode Lengths")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(episode_lengths, alpha=0.7, color='orange')
            ax.set_xlabel("Episode")
            ax.set_ylabel("Steps per Episode")
            ax.set_title("Episode Length Over Time")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

        # Final performance
        recent_rewards = rewards_history[-50:]  # Last 50 episodes
        st.metric("Average Reward (Last 50 episodes)", f"{np.mean(recent_rewards):.2f}")
        st.metric("Success Rate", f"{np.mean([r > 5 for r in recent_rewards]):.1%}")

        # Visualize learned policy
        if method == "Q-Learning":
            st.subheader("Learned Policy")
            policy = agent.get_policy()

            # Create policy grid
            policy_grid = np.zeros((env.size, env.size), dtype=str)
            action_symbols = ['↑', '↓', '←', '→']

            for i in range(env.size):
                for j in range(env.size):
                    state_idx = i * env.size + j
                    if (i, j) == env.goal:
                        policy_grid[i, j] = '🏁'
                    else:
                        policy_grid[i, j] = action_symbols[policy[state_idx]]

            # Display policy
            st.code("\n".join([" ".join(row) for row in policy_grid]), language="text")
            st.info("↑=Up, ↓=Down, ←=Left, →=Right, 🏁=Goal")

def show_rl_classification(df):
    """Demonstrate RL concepts applied to classification tasks."""

    st.subheader("Reinforcement Learning for Classification")

    # Problem setup
    target_col = st.selectbox("Select Target Column", df.columns, key="rl_target")
    if not target_col:
        return

    # Prepare data
    X = df.drop(columns=[target_col]).select_dtypes(include=[np.number])
    y = df[target_col]

    if len(X.columns) == 0:
        st.error("No numeric features found.")
        return

    # Handle missing values and encoding
    X = X.fillna(X.mean())
    if y.dtype == 'object':
        y = pd.factorize(y)[0]  # Convert to numeric

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # RL-inspired classification
    st.write("**RL-Inspired Classification Approach**")
    st.info("""
    This demonstrates how RL concepts can be applied to supervised learning:
    - **Policy**: Decision-making strategy (classifier)
    - **Reward**: Accuracy-based reward signal
    - **Learning**: Policy improvement through experience
    """)

    # Train baseline models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = {
            'accuracy': accuracy,
            'predictions': y_pred
        }

    # Display results
    st.subheader("Model Performance")

    col1, col2 = st.columns(2)
    for i, (name, result) in enumerate(results.items()):
        with col1 if i % 2 == 0 else col2:
            st.metric(f"{name} Accuracy", f"{result['accuracy']:.3f}")

    # RL interpretation
    st.subheader("RL Interpretation")

    # Simulate policy evaluation
    best_model = max(results.items(), key=lambda x: x[1]['accuracy'])[0]
    best_predictions = results[best_model]['predictions']

    # Calculate rewards (accuracy-based)
    rewards = [1 if pred == true else 0 for pred, true in zip(best_predictions, y_test)]
    cumulative_rewards = np.cumsum(rewards)

    # Plot reward accumulation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(cumulative_rewards, linewidth=2)
    ax.set_xlabel("Test Sample")
    ax.set_ylabel("Cumulative Reward (Correct Predictions)")
    ax.set_title("RL-Style Reward Accumulation")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # Feature importance as "state values"
    if hasattr(models[best_model], 'feature_importances_'):
        st.subheader("Feature Importance (State Values)")

        importance_df = pd.DataFrame({
            'Feature': X.columns,
            'Importance': models[best_model].feature_importances_
        }).sort_values('Importance', ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=importance_df.head(10), x='Importance', y='Feature', ax=ax)
        ax.set_title(f"Feature Importance - {best_model}")
        st.pyplot(fig)

    # Summary
    st.subheader("Key RL Concepts Demonstrated")
    st.markdown("""
    - **Environment**: Classification dataset with features as states
    - **Agent**: ML model making predictions (policy)
    - **Actions**: Class predictions
    - **Rewards**: +1 for correct predictions, 0 for incorrect
    - **Learning**: Model training to maximize expected rewards
    - **Policy Evaluation**: Accuracy measurement
    """)

    # Export results
    st.subheader("Export Results")
    results_df = pd.DataFrame({
        'True_Label': y_test,
        'Logistic_Prediction': results['Logistic Regression']['predictions'],
        'RandomForest_Prediction': results['Random Forest']['predictions'],
        'Reward_Logistic': [1 if p == t else 0 for p, t in zip(results['Logistic Regression']['predictions'], y_test)],
        'Reward_RF': [1 if p == t else 0 for p, t in zip(results['Random Forest']['predictions'], y_test)]
    })

    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download RL Classification Results",
        data=csv,
        file_name="rl_classification_results.csv",
        mime="text/csv"
    )