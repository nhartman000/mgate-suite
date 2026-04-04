#!/usr/bin/env python3
import sys
import os
import json
import asyncio
import threading
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import websockets

def run_async_loop(queue, stop_event):
    async def listen():
        uri = "ws://localhost:8000/ws/negotiate"
        while not stop_event.is_set():
            try:
                async with websockets.connect(uri) as websocket:
                    queue.clear()
                    while not stop_event.is_set():
                        data = await websocket.recv()
                        queue.append(json.loads(data))
            except Exception:
                await asyncio.sleep(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(listen())
    except Exception:
        pass
    finally:
        loop.close()

def main():
    queue = []
    stop_event = threading.Event()
    
    t = threading.Thread(target=run_async_loop, args=(queue, stop_event), daemon=True)
    t.start()

    plt.ion()
    fig = plt.figure(figsize=(8, 6))
    fig.canvas.manager.set_window_title('Kadmon Floating Visualizer')
    ax = fig.add_subplot(111, projection='3d')

    print("Floating visualizer started. Waiting for backend connection on ws://localhost:8000/ws/negotiate")

    # Dark mode plot
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.xaxis.pane.set_facecolor('#0a0a0a')
    ax.yaxis.pane.set_facecolor('#0a0a0a')
    ax.zaxis.pane.set_facecolor('#0a0a0a')
    
    # White ax lines
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.zaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='z', colors='white')

    try:
        while True:
            if not plt.fignum_exists(fig.number):
                break
                
            if len(queue) > 0:
                frame = queue[-1]
                queue.clear()
                
                ax.clear()

                user = frame.get('user', [-1.31, 0, 0])
                query = frame.get('query', [-0.75, 0, 0])
                ai = frame.get('ai', [-0.5, 0, 0])

                ax.scatter(*user, c='blue', s=50, label='User (-1.31)')
                ax.scatter(*query, c='orange', s=50, label='Query (-0.75)')
                ax.scatter(*ai, c='green', s=100, label='AI Center')

                x = [user[0], query[0], ai[0], user[0]]
                y = [user[1], query[1], ai[1], user[1]]
                z = [user[2], query[2], ai[2], user[2]]
                ax.plot(x, y, z, c='cyan', linewidth=2)

                ax.set_title(f"Macro-Triangulation - Round {frame.get('round', 0)}\nGap: {frame.get('alignment_gap', 0):.4f}", color='white')
                ax.set_xlim([-2, 0])
                ax.set_ylim([-1, 1])
                ax.set_zlim([-0.5, 1.5])
                ax.set_xlabel('X (Determinism)')
                ax.set_ylabel('Y (Stance)')
                ax.set_zlabel('Z (Abstraction)')
                
                legend = ax.legend(facecolor='#1a1a1a', edgecolor='#222222')
                for text in legend.get_texts():
                    text.set_color('white')
                
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
            else:
                plt.pause(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        plt.close(fig)

if __name__ == '__main__':
    main()
