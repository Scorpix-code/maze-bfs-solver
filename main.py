import tkinter as tk
import tkinter.messagebox as messagebox
from collections import deque
from PIL import Image, ImageTk

# Предупреждение перед запуском игры
def show_warning():
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(
        "Предупреждение",
        "Перед началом убедитесь, что у вас есть изображение 'cockroach.png' в указанной папке.\n"
        "Вы используете сторонние ресурсы. Продолжить?"
    )
    root.destroy()

# Основное меню
class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Меню игры")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')

        label = tk.Label(self.root, text="Добро пожаловать в игру!",
                         font=("Arial", 20), bg='#f0f0f0')
        label.pack(pady=20)

        btn_start = tk.Button(self.root,
                              text="Начать игру", font=("Arial", 14),
                              width=20, command=self.start_game)
        btn_start.pack(pady=10)

        btn_help = tk.Button(self.root, text="Справка: как играть",
                             font=("Arial", 14), width=20, command=self.show_help)
        btn_help.pack(pady=10)

        self.root.mainloop()

    def start_game(self):
        self.root.destroy()
        MazeEditor()

    def show_help(self):
        help_win = tk.Toplevel()
        help_win.title("Справка")
        help_win.geometry("400x250")
        help_win.configure(bg='#f0f0f0')

        rules = (
            "Инструкция:\n\n"
            "• Используйте мышь для рисования или удаления стен.\n"
            "• Щелкните на клетке, чтобы изменить её состояние.\n"
            "• Стартовая позиция — синяя клетка.\n"
            "• Стены — черные клетки.\n"
            "• Нажмите 'Найти выход' для поиска пути.\n"
            "• Желтый — найденный путь.\n"
        )

        label = tk.Label(help_win, text=rules, font=("Arial", 12),
                         bg='#f0f0f0', justify='left')
        label.pack(padx=20, pady=20)

        btn_main = tk.Button(help_win, text="Главная",
                             font=("Arial", 12), command=lambda: self.close_help(help_win))
        btn_main.pack(pady=10)

    def close_help(self, window):
        window.destroy()

# Класс редактора лабиринта
class MazeEditor:
    def __init__(self):
        self.rows = 10
        self.cols = 10
        self.cell_size = 50
        self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = (self.cols // 2, self.rows // 2)
        self.maze[self.start[1]][self.start[0]] = 0

        self.root = tk.Tk()
        self.root.title("Редактор лабиринта")
        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_size,
                                height=self.rows * self.cell_size, bg='white')
        self.canvas.pack()

        btn_main = tk.Button(self.root, text="Главная", font=("Arial", 12),
                             command=self.return_to_main)
        btn_main.pack(pady=5)

        self.rects = []
        for y in range(self.rows):
            row_rects = []
            for x in range(self.cols):
                rect = self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill='white', outline='black'
                )
                self.canvas.tag_bind(rect, "<Button-1>", self.make_toggle(x, y))
                row_rects.append(rect)
            self.rects.append(row_rects)

        # Создаем стены по краям
        for i in range(self.cols):
            self.maze[0][i] = 1
            self.maze[self.rows - 1][i] = 1
        for j in range(self.rows):
            self.maze[j][0] = 1
            self.maze[j][self.cols - 1] = 1

        self.draw_maze()

        # Загрузка изображения таракана
        path_to_image = "cockroach.png"
        try:
            img = Image.open(path_to_image)
            if hasattr(Image, 'Resampling'):
                RESAMPLING_MODE = Image.Resampling.LANCZOS
            resized_img = img.resize((40, 40), RESAMPLING_MODE)
            self.cockroach_img = ImageTk.PhotoImage(resized_img)
        except Exception as e:
            print("Не удалось загрузить изображение:", e)
            self.cockroach_img = None

        self.cockroach_image_obj = None
        self.place_cockroach()

        self.btn_find = tk.Button(self.root, text="Найти выход", command=self.find_path_to_border)
        self.btn_find.pack(pady=10)

        self.btn_reset = tk.Button(self.root, text="Посадить таракана", command=self.place_cockroach)
        self.btn_reset.pack(pady=5)

        self.root.mainloop()

    def make_toggle(self, x, y):
        return lambda event: self.toggle_cell(x, y)

    def place_cockroach(self):
        if self.cockroach_image_obj:
            self.canvas.delete(self.cockroach_image_obj)
        if self.cockroach_img:
            x_start, y_start = self.start
            self.cockroach_image_obj = self.canvas.create_image(
                x_start * self.cell_size + self.cell_size / 2,
                y_start * self.cell_size + self.cell_size / 2,
                image=self.cockroach_img
            )
        self.draw_maze()

    def return_to_main(self):
        self.root.destroy()
        MainMenu()

    def draw_maze(self):
        for y in range(self.rows):
            for x in range(self.cols):
                value = self.maze[y][x]
                if (x, y) == self.start:
                    color = 'blue'
                elif value == 1:
                    color = 'black'
                else:
                    color = 'white'
                self.canvas.itemconfig(self.rects[y][x], fill=color)

    def toggle_cell(self, x, y):
        if (x, y) == self.start:
            return
        self.maze[y][x] = 0 if self.maze[y][x] == 1 else 1
        self.draw_maze()

    def find_path_to_border(self):
        exits = []
        for i in range(self.rows):
            if self.maze[0][i] == 0:
                exits.append((i, 0))
            if self.maze[self.rows - 1][i] == 0:
                exits.append((i, self.rows - 1))
        for j in range(self.cols):
            if self.maze[j][0] == 0:
                exits.append((0, j))
            if self.maze[j][self.cols - 1] == 0:
                exits.append((self.cols - 1, j))
        exits = list(set(exits))
        path = self.bfs(self.start, exits)

        if path:
            self.animate_cockroach_smooth(path)
        else:
            messagebox.showinfo("Тараканчик не смог выбраться", "Тараканчик не смог выбраться из лабиринта 😢")

    def animate_cockroach_smooth(self, path, index=0):
        if index < len(path):
            x, y = path[index]
            # Плавное движение в центр клетки
            self.canvas.coords(
                self.cockroach_image_obj,
                x * self.cell_size + self.cell_size / 2,
                y * self.cell_size + self.cell_size / 2
            )
            # Помечаем путь желтым
            if (x, y) != self.start:
                self.canvas.itemconfig(self.rects[y][x], fill='yellow')
            self.root.after(200, lambda: self.animate_cockroach_smooth(path, index + 1))
        else:
            # Убираем таракана и показываем сообщение
            self.canvas.delete(self.cockroach_image_obj)
            self.cockroach_image_obj = None
            messagebox.showinfo(
                "Таракачик смог убежать от вас",
                f"Он прошел {len(path)} клеток и нашел выход 😃"
            )

    def bfs(self, start, goals):
        queue = deque()
        visited = [[False]*self.cols for _ in range(self.rows)]
        parent = [[None]*self.cols for _ in range(self.rows)]
        sx, sy = start
        queue.append((sx, sy))
        visited[sy][sx] = True
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        goal_set = set(goals)

        while queue:
            x, y = queue.popleft()
            if (x, y) in goal_set:
                path = []
                while (x, y) != self.start:
                    path.append((x, y))
                    x, y = parent[y][x]
                path.append(self.start)
                path.reverse()
                return path
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if not visited[ny][nx] and self.maze[ny][nx] != 1:
                        visited[ny][nx] = True
                        parent[ny][nx] = (x, y)
                        queue.append((nx, ny))
        return None

if __name__ == "__main__":
    show_warning()
    MainMenu()