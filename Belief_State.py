from collections import deque
import random
import tkinter as tk


goal = (
    1, 2, 3,
    4, 5, 6,
    7, 8, 0
)

moves = {
    "Left": -1,
    "Right": 1,
    "Up": -3,
    "Down": 3
}


def goal_test(state):
    return state == goal


def valid_actions(state):
    i = state.index(0)
    actions = []

    if i % 3 != 0:
        actions.append("Left")
    if i % 3 != 2:
        actions.append("Right")
    if i >= 3:
        actions.append("Up")
    if i <= 5:
        actions.append("Down")

    return actions


def swap(state, action):
    state = list(state)
    i_0 = state.index(0)
    new_0 = i_0 + moves[action]
    swapped_tile = state[new_0]

    state[i_0], state[new_0] = state[new_0], state[i_0]

    return tuple(state), swapped_tile


def generate_random_state(steps=20):
    state = goal

    for _ in range(steps):
        action = random.choice(valid_actions(state))
        state, _ = swap(state, action)

    return state


def generate_related_random_state(start, steps=2):
    for _ in range(30):
        state = start

        for _ in range(steps):
            action = random.choice(valid_actions(state))
            state, _ = swap(state, action)

        if state != start:
            return state

    return generate_random_state()


def format_state(state):
    return (
        f"[{state[0]} {state[1]} {state[2]}]\n"
        f"[{state[3]} {state[4]} {state[5]}]\n"
        f"[{state[6]} {state[7]} {state[8]}]"
    )


def format_log_state(state):
    return format_state(state).replace("\n", " | ")


def format_belief_state(belief):
    lines = []

    for index, state in enumerate(sorted(belief), start=1):
        lines.append(f"State {index}: {format_log_state(state)}")

    return "\n".join(lines)


def belief_goal_test(belief):
    return all(goal_test(state) for state in belief)


def belief_transition(belief, action):
    next_states = []

    for state in belief:
        if action in valid_actions(state):
            next_state, _ = swap(state, action)
        else:
            next_state = state

        next_states.append(next_state)

    return frozenset(next_states)


def project_actions_from_start(start, actions):
    states = [start]
    current = start

    for action in actions:
        if action in valid_actions(current):
            current, _ = swap(current, action)

        states.append(current)

    return states


def Belief_State_BFS(start_1, start_2, max_depth=40, max_nodes=200000):
    logs = []
    initial_belief = frozenset([start_1, start_2])

    frontier = deque([(initial_belief, [])])
    explored = {initial_belief}
    expanded_count = 0

    logs.append("=== BELIEF STATE BFS SEARCH LOG ===")
    logs.append("Belief State BFS = dùng BFS trên tập các trạng thái có thể xảy ra.")
    logs.append("Bài này dùng 2 trạng thái random ban đầu.")
    logs.append("Một action được áp dụng cho cả 2 trạng thái.")
    logs.append("Nếu action không hợp lệ với trạng thái nào thì trạng thái đó giữ nguyên.")
    logs.append("Frontier dùng queue: lấy bằng popleft(), thêm bằng append().")
    logs.append(f"max_depth = {max_depth}")
    logs.append("\nInitial Belief State:")
    logs.append(format_belief_state(initial_belief))

    while frontier:
        belief, actions = frontier.popleft()
        expanded_count += 1
        depth = len(actions)

        logs.append("\n--------------------------------")
        logs.append(f"Đang xét Belief State ở depth = {depth}")
        logs.append(f"Số state trong belief = {len(belief)}")
        logs.append(format_belief_state(belief))

        if belief_goal_test(belief):
            logs.append("=> Tất cả state trong Belief State đều là Goal.")
            states_1 = project_actions_from_start(start_1, actions)
            states_2 = project_actions_from_start(start_2, actions)
            return actions, states_1, states_2, logs

        if depth >= max_depth:
            logs.append("-> Không mở rộng vì đạt max_depth.")
            continue

        if expanded_count >= max_nodes:
            logs.append("=> Dừng vì đạt max_nodes.")
            return "failure"

        for action in moves:
            next_belief = belief_transition(belief, action)

            logs.append(f"\n  Thử action {action}:")
            logs.append("  Belief State mới:")
            logs.append(format_belief_state(next_belief))

            if next_belief in explored:
                logs.append("  -> Bỏ qua: Belief State đã xét.")
                continue

            logs.append("  -> Thêm vào frontier.")
            explored.add(next_belief)
            frontier.append((next_belief, actions + [action]))

    logs.append("\n=> Frontier rỗng, không tìm thấy lời giải Belief State.")
    return "failure"


def Belief_State(start_1, start_2, max_depth=40, max_nodes=200000):
    return Belief_State_BFS(start_1, start_2, max_depth, max_nodes)


class BeliefStateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Belief State BFS")

        self.state_1 = generate_random_state()
        self.state_2 = generate_related_random_state(self.state_1)
        self.steps = []
        self.states_1 = []
        self.states_2 = []
        self.index = 0

        title = tk.Label(
            root,
            text="8 Puzzle Solver - Belief State BFS",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        board_frame = tk.Frame(main_frame)
        board_frame.grid(row=0, column=0, padx=10, sticky="n")

        boards = tk.Frame(board_frame)
        boards.pack()

        self.tiles_1 = self.create_board(boards, "Random State 1", 0)
        self.tiles_2 = self.create_board(boards, "Random State 2", 1)

        control_frame = tk.Frame(board_frame)
        control_frame.pack(pady=10)

        self.random_button = tk.Button(
            control_frame,
            text="Tạo 2 random",
            width=16,
            font=("Arial", 11, "bold"),
            command=self.generate_random
        )
        self.random_button.grid(row=0, column=0, padx=5)

        self.solve_button = tk.Button(
            control_frame,
            text="Giải BFS Belief",
            width=18,
            font=("Arial", 11, "bold"),
            command=self.solve
        )
        self.solve_button.grid(row=0, column=1, padx=5)

        self.info = tk.Label(
            board_frame,
            text="Bấm Giải BFS Belief để tìm chuỗi action chung cho cả 2 trạng thái.",
            font=("Arial", 12),
            fg="blue"
        )
        self.info.pack(pady=5)

        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, sticky="n")

        tk.Label(
            right_frame,
            text="Log Belief State BFS",
            font=("Arial", 14, "bold")
        ).pack()

        self.log_text = tk.Text(
            right_frame,
            width=72,
            height=30,
            font=("Consolas", 9)
        )
        self.log_text.pack()

        result_frame = tk.Frame(root)
        result_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(
            result_frame,
            text="Kết quả",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.result_text = tk.Text(
            result_frame,
            width=120,
            height=12,
            font=("Consolas", 10)
        )
        self.result_text.pack(fill="x")

        self.draw_boards()

    def create_board(self, parent, title, column):
        container = tk.Frame(parent)
        container.grid(row=0, column=column, padx=12, sticky="n")

        tk.Label(
            container,
            text=title,
            font=("Arial", 13, "bold")
        ).pack(pady=(0, 6))

        grid = tk.Frame(container)
        grid.pack()

        tiles = []

        for i in range(9):
            tile = tk.Label(
                grid,
                text="",
                width=5,
                height=2,
                font=("Arial", 26, "bold"),
                borderwidth=2,
                relief="ridge",
                bg="white"
            )
            tile.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            tiles.append(tile)

        return tiles

    def draw_board(self, tiles, state):
        for i, value in enumerate(state):
            if value == 0:
                tiles[i].config(text="", bg="lightgray")
            else:
                tiles[i].config(text=str(value), bg="white")

    def draw_boards(self):
        self.draw_board(self.tiles_1, self.state_1)
        self.draw_board(self.tiles_2, self.state_2)

    def generate_random(self):
        self.state_1 = generate_random_state()
        self.state_2 = generate_related_random_state(self.state_1)
        self.steps = []
        self.states_1 = []
        self.states_2 = []
        self.index = 0

        self.draw_boards()
        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.info.config(text="Đã tạo 2 trạng thái random.")

    def solve(self):
        self.log_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        result = Belief_State_BFS(self.state_1, self.state_2)

        if result == "failure":
            self.info.config(text="Không tìm thấy lời giải cho Belief State.")
            return

        self.steps, self.states_1, self.states_2, logs = result
        self.index = 0

        self.log_text.insert(tk.END, "\n".join(logs))
        self.log_text.insert(tk.END, "\n\n=== SOLUTION PATH ANIMATION ===\n\n")
        self.log_text.see(tk.END)

        self.show_result_path()

        self.random_button.config(state="disabled")
        self.solve_button.config(state="disabled")
        self.show_step()

    def show_result_path(self):
        self.result_text.insert(tk.END, "Thuật toán: Belief State BFS\n")
        self.result_text.insert(tk.END, f"Tổng số bước đi chung: {len(self.steps)}\n")

        self.result_text.insert(tk.END, "\nTrạng thái ban đầu 1:\n")
        self.result_text.insert(tk.END, format_state(self.states_1[0]))
        self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, "\nTrạng thái ban đầu 2:\n")
        self.result_text.insert(tk.END, format_state(self.states_2[0]))
        self.result_text.insert(tk.END, "\n\n")

        for i in range(1, len(self.states_1)):
            self.result_text.insert(tk.END, f"Step {i}: {self.steps[i - 1]}\n")

            self.result_text.insert(tk.END, "State 1:\n")
            self.result_text.insert(tk.END, format_state(self.states_1[i]))
            self.result_text.insert(tk.END, "\n\n")

            self.result_text.insert(tk.END, "State 2:\n")
            self.result_text.insert(tk.END, format_state(self.states_2[i]))
            self.result_text.insert(tk.END, "\n\n")

        if goal_test(self.states_1[-1]) and goal_test(self.states_2[-1]):
            self.result_text.insert(tk.END, "Cả 2 trạng thái đã tới đích.\n")
        else:
            self.result_text.insert(tk.END, "Chưa đưa được cả 2 trạng thái tới đích.\n")

    def show_step(self):
        if self.index < len(self.states_1):
            self.state_1 = self.states_1[self.index]
            self.state_2 = self.states_2[self.index]
            self.draw_boards()

            if self.index == 0:
                self.info.config(text=f"Initial Belief State | Total moves: {len(self.steps)}")
                self.log_text.insert(
                    tk.END,
                    "Step 0 Solution: Initial Belief State\n"
                    f"State 1:\n{format_state(self.state_1)}\n\n"
                    f"State 2:\n{format_state(self.state_2)}\n\n"
                )
            else:
                move = self.steps[self.index - 1]
                previous_1 = self.states_1[self.index - 1]
                previous_2 = self.states_2[self.index - 1]

                self.info.config(
                    text=f"Step {self.index}/{len(self.steps)} | Action chung: {move}"
                )

                self.log_text.insert(
                    tk.END,
                    f"Step {self.index} Solution: Action {move}\n"
                    "State 1:\n"
                    f"{self.describe_transition(previous_1, self.state_1, move)}"
                    f"{format_state(self.state_1)}\n"
                    "\n"
                    "State 2:\n"
                    f"{self.describe_transition(previous_2, self.state_2, move)}"
                    f"{format_state(self.state_2)}\n"
                    "\n"
                )

            self.log_text.see(tk.END)
            self.index += 1
            self.root.after(700, self.show_step)
        else:
            self.random_button.config(state="normal")
            self.solve_button.config(state="normal")

            if goal_test(self.state_1) and goal_test(self.state_2):
                self.info.config(text="Đã giải xong cả 2 trạng thái Belief State!")
            else:
                self.info.config(text="Belief State chưa đưa cả 2 trạng thái tới đích.")

    def describe_transition(self, previous_state, current_state, action):
        if action not in valid_actions(previous_state):
            return "Action không hợp lệ, trạng thái giữ nguyên.\n"

        new_zero = current_state.index(0)
        swapped_tile = previous_state[new_zero]
        return f"Hoán đổi 0 với {swapped_tile}\n"


if __name__ == "__main__":
    root = tk.Tk()
    app = BeliefStateApp(root)
    root.mainloop()
