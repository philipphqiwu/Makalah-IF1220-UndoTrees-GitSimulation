import tkinter as tk
from tkinter import messagebox

class TreeNode:
    def __init__(self, text_state, parent=None):
        self.text_state = text_state
        self.parent = parent
        self.children = []

    def add_state(self, new_text):
        new_node = TreeNode(new_text, parent=self)
        self.children.append(new_node)
        return new_node

class UndoTreeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Undo Tree Text Editor")
        self.master.configure(bg='#0f1117')  
        self.master.geometry("1200x600")

        self.root_node = TreeNode("")
        self.current_node = self.root_node

        self.last_text = self.root_node.text_state

        # Stack for redo
        self.redo_stack = []

        # Manual 50-50 split
        self.editor_frame = tk.Frame(self.master, bg='#1e1e2e')
        self.editor_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        self.tree_frame = tk.Frame(self.master, bg='#0f1117')
        self.tree_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        # Editor widgets
        self.text_label = tk.Label(self.editor_frame, text="Current Text:", bg='#1e1e2e', fg='#f1f1f1', font=("Helvetica", 32))
        self.text_label.pack(anchor='w', padx=10, pady=(10, 0))

        self.text_display = tk.Text(self.editor_frame, height=10, bg='#2b2d42', fg='#ffffff', insertbackground='white', font=("Consolas", 32), bd=0, relief=tk.FLAT)
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.text_display.bind('<KeyRelease-Return>', self.on_text_change)
        self.text_display.bind('<KeyRelease-space>', self.on_text_change)
        self.text_display.bind('<KeyRelease>', self.track_last_text)
        self.text_display.bind('<Control-z>', self.ctrl_z_handler)
        self.text_display.bind('<Control-y>', self.ctrl_y_handler)

        button_frame = tk.Frame(self.editor_frame, bg='#1e1e2e')
        button_frame.pack(anchor='w', padx=10, pady=(0, 10))

        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo, bg='#4c566a', fg='white', font=("Helvetica", 30, "bold"), activebackground='#5e81ac')
        self.undo_button.pack(side=tk.LEFT, padx=(0, 10))

        self.redo_button = tk.Button(button_frame, text="Redo", command=self.redo, bg='#4c566a', fg='white', font=("Helvetica", 30, "bold"), activebackground='#88c0d0')
        self.redo_button.pack(side=tk.LEFT)

        # Tree view widgets
        self.tree_label = tk.Label(self.tree_frame, text="Undo Tree", bg='#0f1117', fg='#81a1c1', font=("Helvetica", 32, "bold"))
        self.tree_label.pack(pady=(10, 5))
        self.tree_listbox = tk.Listbox(self.tree_frame, bg='#1a1d23', fg='#d8dee9', selectbackground='#5e81ac', font=("Courier", 20), bd=0, relief=tk.FLAT)
        self.tree_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.tree_listbox.bind('<<ListboxSelect>>', self.on_tree_select)

        self.update_text_display()
        self.update_tree_view()

    def update_text_display(self):
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, self.current_node.text_state)
        self.last_text = self.current_node.text_state

    def track_last_text(self, event=None):
        self.last_text = self.text_display.get("1.0", tk.END).rstrip('\n')

    def on_text_change(self, event=None):
        new_text = self.text_display.get("1.0", tk.END).rstrip('\n')
        if new_text != self.last_text:
            self.current_node = self.current_node.add_state(new_text)
            self.last_text = new_text
            self.redo_stack.clear()
            self.update_tree_view()

    def ctrl_z_handler(self, event):
        self.undo()
        return 'break'

    def ctrl_y_handler(self, event):
        self.redo()
        return 'break'

    def undo(self):
        if self.current_node.parent:
            self.redo_stack.append(self.current_node)
            self.current_node = self.current_node.parent
            self.update_text_display()
            self.update_tree_view()
        else:
            messagebox.showinfo("Undo", "Already at the root node.")

    def redo(self):
        if self.redo_stack:
            redo_node = self.redo_stack.pop()
            if redo_node.parent == self.current_node:
                self.current_node = redo_node
                self.update_text_display()
                self.update_tree_view()
            else:
                messagebox.showinfo("Redo", "Redo path no longer valid.")
        else:
            messagebox.showinfo("Redo", "Nothing to redo.")

    def update_tree_view(self):
        self.tree_listbox.delete(0, tk.END)
        self.node_list = []
        self.build_tree_list(self.root_node, "", True)

    def build_tree_list(self, node, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        display = f"{prefix}{connector}{repr(node.text_state)}"
        if node == self.current_node:
            display += "  <-- CURRENT"
        self.tree_listbox.insert(tk.END, display)
        self.node_list.append(node)

        child_count = len(node.children)
        for i, child in enumerate(node.children):
            next_prefix = prefix + ("    " if is_last else "│   ")
            self.build_tree_list(child, next_prefix, i == child_count - 1)

    def on_tree_select(self, event):
        if not self.tree_listbox.curselection():
            return
        index = self.tree_listbox.curselection()[0]
        selected_node = self.node_list[index]
        self.current_node = selected_node
        self.update_text_display()
        self.update_tree_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = UndoTreeApp(root)
    root.mainloop()