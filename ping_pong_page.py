import streamlit as st
import streamlit.components.v1 as components


def render_ping_pong():
    st.title('Ping Pong')
    st.caption('Move the paddle with your mouse or arrow keys. First to 5 wins.')

    components.html(
        """
        <style>
            .pingpong-container {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 8px 0 16px 0;
            }
            canvas {
                border: 2px solid #1f2937;
                border-radius: 8px;
                background: #f8fafc;
            }
            .pingpong-help {
                font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
                color: #334155;
                font-size: 14px;
                margin-top: 8px;
                text-align: center;
            }
        </style>
        <div class="pingpong-container">
            <canvas id="pong" width="720" height="420"></canvas>
        </div>
        <div class="pingpong-help">Press Space to pause/resume.</div>
        <script>
            const canvas = document.getElementById('pong');
            const ctx = canvas.getContext('2d');

            const state = {
                paused: false,
                player: { x: canvas.width / 2 - 50, y: canvas.height - 18, w: 100, h: 10, speed: 8 },
                cpu: { x: canvas.width / 2 - 40, y: 8, w: 80, h: 10, speed: 5 },
                ball: { x: canvas.width / 2, y: canvas.height / 2, r: 8, vx: 4, vy: 4 },
                score: { player: 0, cpu: 0, max: 5 },
            };

            const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

            const resetBall = (direction = 1) => {
                state.ball.x = canvas.width / 2;
                state.ball.y = canvas.height / 2;
                state.ball.vx = 4 * (Math.random() > 0.5 ? 1 : -1);
                state.ball.vy = 4 * direction;
            };

            const drawNet = () => {
                ctx.fillStyle = '#cbd5f5';
                for (let i = 0; i < canvas.height; i += 18) {
                    ctx.fillRect(canvas.width / 2 - 2, i, 4, 10);
                }
            };

            const drawScores = () => {
                ctx.fillStyle = '#0f172a';
                ctx.font = '600 20px ui-sans-serif, system-ui, -apple-system, sans-serif';
                ctx.fillText(`You ${state.score.player}`, 24, canvas.height / 2 + 40);
                ctx.fillText(`CPU ${state.score.cpu}`, canvas.width - 110, canvas.height / 2 + 40);
            };

            const draw = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                drawNet();

                ctx.fillStyle = '#1d4ed8';
                ctx.fillRect(state.player.x, state.player.y, state.player.w, state.player.h);

                ctx.fillStyle = '#0ea5e9';
                ctx.fillRect(state.cpu.x, state.cpu.y, state.cpu.w, state.cpu.h);

                ctx.beginPath();
                ctx.fillStyle = '#111827';
                ctx.arc(state.ball.x, state.ball.y, state.ball.r, 0, Math.PI * 2);
                ctx.fill();

                drawScores();

                if (state.paused) {
                    ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = '#f8fafc';
                    ctx.font = '700 28px ui-sans-serif, system-ui, -apple-system, sans-serif';
                    ctx.fillText('Paused', canvas.width / 2 - 52, canvas.height / 2);
                }

                if (state.score.player === state.score.max || state.score.cpu === state.score.max) {
                    ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = '#f8fafc';
                    ctx.font = '700 24px ui-sans-serif, system-ui, -apple-system, sans-serif';
                    const winner = state.score.player === state.score.max ? 'You win!' : 'CPU wins!';
                    ctx.fillText(winner, canvas.width / 2 - 60, canvas.height / 2 - 8);
                    ctx.font = '500 16px ui-sans-serif, system-ui, -apple-system, sans-serif';
                    ctx.fillText('Reload the page to play again', canvas.width / 2 - 112, canvas.height / 2 + 20);
                }
            };

            const update = () => {
                if (state.paused) return;
                if (state.score.player === state.score.max || state.score.cpu === state.score.max) return;

                state.ball.x += state.ball.vx;
                state.ball.y += state.ball.vy;

                if (state.ball.x - state.ball.r <= 0 || state.ball.x + state.ball.r >= canvas.width) {
                    state.ball.vx *= -1;
                }

                if (state.ball.y - state.ball.r <= state.cpu.y + state.cpu.h) {
                    if (state.ball.x > state.cpu.x && state.ball.x < state.cpu.x + state.cpu.w) {
                        state.ball.vy *= -1;
                        state.ball.y = state.cpu.y + state.cpu.h + state.ball.r;
                    } else {
                        state.score.player += 1;
                        resetBall(1);
                    }
                }

                if (state.ball.y + state.ball.r >= state.player.y) {
                    if (state.ball.x > state.player.x && state.ball.x < state.player.x + state.player.w) {
                        state.ball.vy *= -1;
                        const offset = (state.ball.x - (state.player.x + state.player.w / 2)) / (state.player.w / 2);
                        state.ball.vx = 5 * offset;
                        state.ball.y = state.player.y - state.ball.r;
                    } else {
                        state.score.cpu += 1;
                        resetBall(-1);
                    }
                }

                const target = state.ball.x - state.cpu.w / 2;
                if (state.ball.y < canvas.height / 2) {
                    state.cpu.x += clamp(target - state.cpu.x, -state.cpu.speed, state.cpu.speed);
                    state.cpu.x = clamp(state.cpu.x, 0, canvas.width - state.cpu.w);
                }
            };

            const loop = () => {
                update();
                draw();
                requestAnimationFrame(loop);
            };

            const handleMouse = (event) => {
                const rect = canvas.getBoundingClientRect();
                const x = event.clientX - rect.left;
                state.player.x = clamp(x - state.player.w / 2, 0, canvas.width - state.player.w);
            };

            let leftPressed = false;
            let rightPressed = false;

            const handleKeys = () => {
                if (leftPressed) {
                    state.player.x = clamp(state.player.x - state.player.speed, 0, canvas.width - state.player.w);
                }
                if (rightPressed) {
                    state.player.x = clamp(state.player.x + state.player.speed, 0, canvas.width - state.player.w);
                }
                requestAnimationFrame(handleKeys);
            };

            document.addEventListener('mousemove', handleMouse);
            document.addEventListener('keydown', (event) => {
                if (event.code === 'ArrowLeft') leftPressed = true;
                if (event.code === 'ArrowRight') rightPressed = true;
                if (event.code === 'Space') state.paused = !state.paused;
            });
            document.addEventListener('keyup', (event) => {
                if (event.code === 'ArrowLeft') leftPressed = false;
                if (event.code === 'ArrowRight') rightPressed = false;
            });

            handleKeys();
            resetBall(1);
            loop();
        </script>
        """,
        height=520,
    )
