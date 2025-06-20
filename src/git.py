import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random
import string

# Generate a short random commit hash
def generate_commit_id():
    return ''.join(random.choices(string.hexdigits[:16], k=7))

class CommitNode:
    commit_counter = 0

    def __init__(self, message, parents=None, branch='main'):
        self.id = generate_commit_id()
        self.message = message
        self.parents = parents if parents else []
        self.children = []
        self.branch = branch
        self.order = CommitNode.commit_counter
        CommitNode.commit_counter += 1

    def add_child(self, message, branch=None):
        new_commit = CommitNode(message, parents=[self], branch=branch or self.branch)
        self.children.append(new_commit)
        return new_commit

class GitSimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Git Simulation")
        self.master.geometry("1200x600")
        self.master.configure(bg='#121212')

        self.branches = {'main': []}
        self.current_branch = 'main'
        self.head = None

        # Layout frames (updated sizes)
        self.left_frame = tk.Frame(self.master, bg='#1e1e2e')
        self.left_frame.place(relx=0, rely=0, relwidth=0.2, relheight=1)

        self.middle_frame = tk.Frame(self.master, bg='#121212')
        self.middle_frame.place(relx=0.2, rely=0, relwidth=0.5, relheight=1)

        self.right_frame = tk.Frame(self.master, bg='#262626')
        self.right_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)


        # Branch view
        self.branch_label = tk.Label(self.left_frame, text="Branches", bg='#1e1e2e', fg='white', font=("Helvetica", 14))
        self.branch_label.pack(pady=10)
        self.branch_listbox = tk.Listbox(self.left_frame, bg='#1e1e2e', fg='white', font=('Courier', 12))
        self.branch_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Commit history
        self.commit_label = tk.Label(self.middle_frame, text="Commits", bg='#121212', fg='white', font=("Helvetica", 14))
        self.commit_label.pack(pady=10)
        self.commit_listbox = tk.Listbox(self.middle_frame, bg='#121212', fg='white', font=('Courier', 12))
        self.commit_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Control buttons and log
        self.controls_label = tk.Label(self.right_frame, text="Controls & Log", bg='#262626', fg='white', font=("Helvetica", 14))
        self.controls_label.pack(pady=10)

        self.commit_button = tk.Button(self.right_frame, text="Commit", command=self.commit, font=("Helvetica", 12), bg='#3c3c3c', fg='white')
        self.commit_button.pack(pady=5)

        self.branch_button = tk.Button(self.right_frame, text="Create Branch", command=self.create_branch, font=("Helvetica", 12), bg='#3c3c3c', fg='white')
        self.branch_button.pack(pady=5)

        self.switch_button = tk.Button(self.right_frame, text="Switch Branch", command=self.switch_branch, font=("Helvetica", 12), bg='#3c3c3c', fg='white')
        self.switch_button.pack(pady=5)

        self.merge_button = tk.Button(self.right_frame, text="Merge", command=self.merge_branch, font=("Helvetica", 12), bg='#3c3c3c', fg='white')
        self.merge_button.pack(pady=5)

        self.log_area = tk.Text(self.right_frame, height=10, bg='#2e2e2e', fg='white', font=('Courier', 10), state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.init_repo()

    def init_repo(self):
        root_commit = CommitNode("Initial commit", branch='main')
        self.branches['main'].append(root_commit)
        self.head = root_commit
        self.update_view()

    def commit(self):
        message = simpledialog.askstring("Commit Message", "Enter commit message:")
        if message:
            new_commit = self.head.add_child(message, branch=self.current_branch)
            self.branches[self.current_branch].append(new_commit)
            self.head = new_commit
            self.update_view()

    def create_branch(self):
        name = simpledialog.askstring("New Branch", "Enter new branch name:")
        if name and name not in self.branches:
            self.branches[name] = [self.head]
            self._log(f"Branch '{name}' created at commit {self.head.id}\n")
            self.update_view()

    def switch_branch(self):
        name = simpledialog.askstring("Switch Branch", "Enter branch name:")
        if name in self.branches:
            self.current_branch = name
            self.head = self.branches[name][-1]
            self._log(f"Switched to branch '{name}'\n")
            self.update_view()
        else:
            messagebox.showerror("Error", "Branch does not exist.")

    def merge_branch(self):
        name = simpledialog.askstring("Merge Branch", "Enter branch to merge:")
        if name in self.branches and name != self.current_branch:
            other_head = self.branches[name][-1]
            merge_commit = CommitNode(f"Merge {name} into {self.current_branch}", parents=[self.head, other_head], branch=self.current_branch)
            self.head.children.append(merge_commit)
            other_head.children.append(merge_commit)
            self.branches[self.current_branch].append(merge_commit)
            self.head = merge_commit
            self.update_view()
            self._log(f"Merged branch '{name}' into '{self.current_branch}'\n")
        else:
            messagebox.showerror("Error", "Invalid branch.")

    def _log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def update_view(self):
        self.commit_listbox.delete(0, tk.END)
        self.branch_listbox.delete(0, tk.END)

        for branch, commits in self.branches.items():
            head_marker = " <-- HEAD" if branch == self.current_branch else ""
            self.branch_listbox.insert(tk.END, f"{branch}{head_marker}")

        self.node_lines = []
        self.visited = set()
        self._build_commit_tree(self.branches['main'][0])

        for line in self.node_lines:
            self.commit_listbox.insert(tk.END, line)

    def _build_commit_tree(self, node, prefix="", is_last=True, visited=None):
        if visited is None:
            visited = set()

        if node in visited:
            return
        visited.add(node)

        connector = "└── " if is_last else "├── "
        label = f"{prefix}{connector}[{node.branch}] {node.id[:7]}: {node.message}"
        if node == self.head:
            label += "  <-- HEAD"
        self.node_lines.append(label)

        children = sorted(node.children, key=lambda c: c.order)
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            next_prefix = prefix + ("    " if is_last else "│   ")
            self._build_commit_tree(child, next_prefix, is_last_child, visited)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitSimulatorApp(root)
    root.mainloop()