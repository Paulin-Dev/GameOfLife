#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Built-in imports
from os import listdir, mkdir, remove 
from os.path import dirname, isdir, join, realpath 
from math import ceil

# Third-party imports
import cv2
import matplotlib.pyplot as plt
import matplotlib.backend_bases as mbb
import numpy as np

# Constants
APP_PATH      = dirname(realpath(__file__))
BOARD_SIZE    = (50, 50)
SPEED         = 20
FPS           = 10
FILENAME      = 'export'
WIDTH, HEIGHT = 2000, 2000
DPI           = 400

'''
Game Of Life

Rules:
  - A cell with less than two live neighbours dies, as if caused by underpopulation.
  - A cell with two or three live neighbours lives on to the next generation.
  - A cell with more than three live neighbours dies, as if by overpopulation.
  - If a dead cell has exactly three live neighbours, it becomes a live cell, as if by reproduction.
'''


class Board:
    def __init__(self, size: tuple, speed: int, living_rate) -> None:
        self.size        = size[1], size[0]
        self.speed       = ceil(speed) if  0 < ceil(speed) <= 1_000 else SPEED
        self.living_rate = living_rate if 0 < living_rate < 1 else .2
        self.init_board()
        self.init_plot()
        
    def init_board(self, random: bool = False) -> None:
        if random:
            self.board = np.random.choice([False, True], size=self.size, p=[1-self.living_rate, self.living_rate])
        else:
            self.board = np.zeros(self.size, dtype=bool)
        
    def init_plot(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.fig.canvas.toolbar.pack_forget()
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.display()
        
    def display(self, generation: int = None) -> None:
        self.ax.clear()
        self.ax.axis('off')
        if generation is not None:
            self.ax.text(0, 1, str(generation), color='green', fontsize=15, va='top')
            
        self.ax.imshow(self.board, cmap='binary')
        self.fig.canvas.draw()
        plt.pause(1 / self.speed)
        

class VideoManager:
    def __init__(self, filename: str, fps: int) -> None:
        self.check_frames_dir()
        self.clear_frames()
        self.filename = filename
        self.fps      = ceil(fps) if 0 < ceil(fps) < 100 else FPS
        
    def check_frames_dir(self) -> None:
        if not isdir(join(APP_PATH, 'frames')):
            mkdir(join(APP_PATH, 'frames'))
        
    def clear_frames(self) -> None:
        for file in listdir(join(APP_PATH, 'frames')):
            remove(join(APP_PATH, 'frames', file))

    def save_video(self) -> None:
        out = cv2.VideoWriter(f'{self.filename}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (WIDTH, HEIGHT))
        try:
            for i in range(len(listdir(join(APP_PATH, 'frames')))):
                out.write(cv2.imread(join(APP_PATH, 'frames', f'{i}.png')))
        finally:
            out.release()


class Simulation(Board, VideoManager):
    def __init__(self, board_size: tuple = BOARD_SIZE, speed: int = SPEED, living_rate: float = .2, export: bool = False, filename: str = FILENAME, fps: int = FPS) -> None:
        super().__init__(board_size, speed, living_rate)
        super(Board, self).__init__(filename, fps)

        self.export     = export
        self.started    = False
        self.generation = 0

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        plt.show()
        
    def on_click(self, event: mbb.MouseEvent) -> None:
        if not self.started:
            self.board[round(event.ydata), round(event.xdata)] = False if self.board[round(event.ydata), round(event.xdata)] else True
            self.display(self.generation)

    def on_key_press(self, event: mbb.MouseEvent) -> None:
        if event.key == ' ':
            if not self.started:
                self.start()
            else:
                self.started = False

        elif not self.started:
            if event.key == 'c' :
                self.init_board()
                self.display()
            
            elif event.key == 'r' :
                self.init_board(random=True)
                self.display()
                
            elif event.key == 'e' and self.export:
                self.save_video()
                
            if event.key in ['c', 'r', 'e']:
                self.clear_frames()
                self.generation = 0

    def start(self) -> None:
        self.started = True
        while self.started:
            backup = self.board.copy()
            self.evolve()
            if np.array_equal(backup, self.board):
                self.started = False
            else:
                self.generation += 1
                self.display(self.generation)
                if np.all(self.board == 0):
                    self.generation = 0
                    self.started = False
           

    def evolve(self) -> None:
        board = self.board.astype(int)
        neigh = np.zeros(board.shape)
        neigh[1:-1, 1:-1] = (
            board[:-2,:-2]  + board[:-2,1:-1] + board[:-2,2:]  +
            board[1:-1,:-2] +                   board[1:-1,2:] + 
            board[2:,:-2]   + board[2:,1:-1]  + board[2:,2:]
        )
        
        self.board = np.logical_or(neigh==3, np.logical_and(board==1, neigh==2))
        if self.export:
            plt.savefig(join(APP_PATH, 'frames', f'{self.generation}.png'), dpi=DPI)
