from pathlib import Path
import sqlite3
from datetime import datetime, timedelta, timezone
import tempfile

import streamlit as st
import streamlit.components.v1 as components


# ============================================================================
# CẤU HÌNH TRANG
# ============================================================================

st.set_page_config(
    page_title="Chuyện tình chúng mình",
    page_icon="💗",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 8% 12%, rgba(255,226,237,.85) 0%, rgba(255,226,237,.28) 32%, transparent 68%),
            radial-gradient(ellipse at 94% 40%, rgba(238,226,255,.8) 0%, rgba(238,226,255,.26) 36%, transparent 72%),
            radial-gradient(ellipse at 50% 108%, rgba(255,236,219,.55) 0%, rgba(255,236,219,.16) 42%, transparent 78%),
            linear-gradient(125deg, #fff5f4, #faf0f8 55%, #fff9f1);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1050px;
        padding: 1rem 1rem 2rem;
    }

    @media (max-width: 600px) {
        [data-testid="stMainBlockContainer"] {
            padding: .6rem .5rem 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# TOÀN BỘ GIAO DIỆN
#
# Dùng custom component có giao thức báo chiều cao cho Streamlit.
# Không dùng components.html với chiều cao lớn cố định.
# ============================================================================

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<link
    href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Nunito:wght@400;600;700;800&display=swap"
    rel="stylesheet"
>


<style>
:root {
    --rose: #a44365;
    --ink: #624251;
    --muted: #856673;
    --line: #ead1dc;
    --gold: #b58b54;
}

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    background: transparent;
    color: var(--ink);
    font-family: "Nunito", system-ui, sans-serif;
}

body {
    padding: 12px 8px 24px;
    /* Không gian 3D cho các thẻ nghiêng theo chuột */
    perspective: 1200px;
}

button,
input,
select,
textarea {
    font: inherit;
}

button {
    cursor: pointer;
    color: var(--rose);
}

button:focus-visible,
select:focus-visible,
textarea:focus-visible,
a:focus-visible {
    outline: 3px solid #b65e82;
    outline-offset: 4px;
}

main {
    position: relative;
    isolation: isolate;
    max-width: 900px;
    margin: auto;

    display: flex;
    flex-direction: column;
    gap: 24px;

    transform-origin: 50% 0;
    animation: cardEntrance 1.15s cubic-bezier(.22, .8, .25, 1) both;
}

/* --------------------------------------------------------------------------
   ÁNH SÁNG VÀ SAO
--------------------------------------------------------------------------- */

.ambient {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: -1;

    background:
        radial-gradient(ellipse at 12% 18%, rgba(255, 184, 214, .3) 0%, rgba(255, 184, 214, .1) 34%, transparent 68%),
        radial-gradient(ellipse at 90% 45%, rgba(214, 190, 255, .28) 0%, rgba(214, 190, 255, .1) 38%, transparent 72%),
        radial-gradient(ellipse at 25% 80%, rgba(255, 222, 170, .24) 0%, rgba(255, 222, 170, .08) 40%, transparent 74%);
}

.star {
    position: absolute;
    color: var(--gold);
    text-shadow:
        0 0 6px rgba(255, 255, 255, .95),
        0 0 14px rgba(255, 212, 148, .55);
    animation: twinkle var(--speed) ease-in-out infinite;
    animation-delay: var(--delay);
}

.orb {
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    filter: blur(45px);
    opacity: .22;
    background: #efb1cd;
    animation: drift 15s ease-in-out infinite alternate;
}

.orb.two {
    top: 45%;
    right: -100px;
    background: #c6b3ea;
    animation-delay: -7s;
}

/* Charm: vị trí giữ riêng, hình bên trong mới chuyển động. */
.charm {
    position: absolute;
    display: block;
    pointer-events: none;
    user-select: none;
    transform: translate(-50%, -50%);
}

.charm-icon {
    display: block;
    font-size: var(--size);
    line-height: 1.3;
    opacity: .52;

    filter:
        drop-shadow(0 0 7px rgba(255, 255, 255, .95))
        drop-shadow(0 0 15px rgba(236, 151, 188, .35));

    animation: charmFloat var(--duration) ease-in-out infinite;
    animation-delay: var(--delay);
}

.charm::after {
    content: "✦";
    position: absolute;
    right: -9px;
    top: -7px;

    font-size: 13px;
    color: #bb8d4e;
    text-shadow:
        0 0 5px white,
        0 0 12px rgba(255, 209, 127, .7);

    animation: charmGlint 3.8s ease-in-out infinite;
    animation-delay: var(--delay);
}

.fairy-light {
    position: absolute;
    width: var(--size);
    height: var(--size);
    border-radius: 50%;
    pointer-events: none;
    background: #fffdf4;

    box-shadow:
        0 0 4px 1px rgba(255, 255, 255, .95),
        0 0 11px 3px rgba(255, 195, 215, .65);

    animation: fairyGlow var(--duration) ease-in-out infinite;
    animation-delay: var(--delay);
}

/* --------------------------------------------------------------------------
   TIÊU ĐỀ VÀ NHẠC
--------------------------------------------------------------------------- */

.hero {
    text-align: center;
    padding: 22px 8px 4px;
}

.eyebrow {
    font-size: .67rem;
    letter-spacing: .22em;
    font-weight: 800;
    color: var(--muted);
}

h1 {
    font-family: "Great Vibes", cursive;
    font-size: clamp(3.1rem, 7vw, 4.8rem);
    font-weight: 400;
    line-height: 1.25;
    margin: 16px 0 8px;
    background: linear-gradient(120deg, #a44365, #d47a98, #b58b54, #a44365);
    background-size: 300% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 18px rgba(164, 67, 101, .22));
    animation: titleShimmer 7s linear infinite;
}

.subtitle {
    font-size: .93rem;
    color: var(--muted);
    line-height: 1.7;
    margin: 0;
}

.music {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;

    margin-top: 18px;
    min-height: 44px;
    padding: 10px 18px;

    border: 1px solid var(--line);
    border-radius: 99px;
    background: #ffffffb0;
    font-size: .8rem;

    transition: background .2s ease, box-shadow .2s ease;
}

.music:hover {
    background: #fff9fc;
    box-shadow: 0 5px 18px #b4648315;
}

.music:disabled {
    cursor: wait;
    opacity: .7;
}

.equalizer {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 16px;
}

.equalizer i {
    height: 5px;
    width: 3px;
    border-radius: 3px;
    background: #b46483;
}

.music.playing i {
    animation: equalize .8s ease-in-out infinite alternate;
}

.music i:nth-child(2) {
    animation-delay: -.4s;
}

.music i:nth-child(3) {
    animation-delay: -.2s;
}

.audio-frame {
    position: absolute;
    left: 0;
    top: 0;
    width: 1px;
    height: 1px;
    overflow: hidden;
    opacity: 0;
    pointer-events: none;
}

.audio-frame iframe {
    border: 0;
    width: 166px;
    height: 166px;
}

.music-note {
    font-size: .74rem;
    color: var(--muted);
    margin: 9px 0 0;
    min-height: 18px;
}

.music-note a {
    color: var(--rose);
}

/* --------------------------------------------------------------------------
   HAI THẺ TÊN
--------------------------------------------------------------------------- */

.profiles {
    position: relative;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: stretch;
    gap: 24px;
}

.profile {
    min-width: 0;
    position: relative;

    display: grid;
    grid-template-rows: 82px 76px 34px 1fr auto;

    padding: 28px 28px 20px;
    text-align: center;

    border: 1px solid #e9cbd9;
    border-radius: 28px;
    background: linear-gradient(140deg, #fffffff0, #fff4fae0);
    box-shadow: 0 12px 30px #9e47660c;

    /* 3D: nghiêng theo chuột, có chiều sâu */
    transform-style: preserve-3d;
    will-change: transform;
    transition: transform .18s ease, box-shadow .3s ease;
}

.profile:hover {
    box-shadow: 0 22px 44px #9e476626;
}

.profile::after {
    content: "✧";
    position: absolute;
    right: 20px;
    top: 16px;
    font-size: 24px;
    color: var(--gold);
    animation: twinkle 4s ease-in-out infinite;
}

.avatar {
    display: grid;
    place-items: center;

    width: 76px;
    height: 76px;
    margin: auto;

    border-radius: 50%;
    font-size: 2.6rem;
    background: radial-gradient(circle at 30% 25%, white, #f8dce8);
    box-shadow: 0 0 0 6px #ffffffa0, 0 7px 20px #b4648314;

    /* Nổi lên khỏi mặt thẻ */
    transform: translateZ(40px);
}

.profile h2 {
    display: grid;
    place-items: center;

    font-family: "Great Vibes", cursive;
    font-size: clamp(2rem, 4vw, 2.7rem);
    font-weight: 400;
    line-height: 1.15;
    color: var(--rose);

    margin: 0;
    overflow-wrap: anywhere;
}

.role {
    font-size: .76rem;
    font-weight: 800;
    color: var(--rose);
    margin: 0;
    letter-spacing: .06em;
}

.details {
    display: grid;
    grid-template-columns: 70px minmax(0, 1fr);
    gap: 12px 10px;
    align-content: start;

    text-align: left;
    line-height: 1.75;
    font-size: .87rem;

    border-top: 1px solid var(--line);
    padding-top: 18px;
    margin: 12px 0 20px;
    min-height: 126px;
}

.details dt {
    color: var(--muted);
}

.details dd {
    margin: 0;
    overflow-wrap: anywhere;
}

.mood {
    width: 100%;
    min-height: 44px;
    padding: 10px;

    border: 1px solid var(--line);
    border-radius: 14px;
    background: #fff9fc;

    font-size: .84rem;
    transition: background .2s ease;
}

.mood:hover {
    background: #fce7f0;
}

.mood-text {
    font-size: .83rem;
    line-height: 1.65;
    color: var(--muted);

    margin: 12px 0 0;
    min-height: 66px;
}

.bridge {
    position: absolute;
    left: 50%;
    top: 46%;
    transform: translate(-50%, -50%);
    z-index: 2;

    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;

    background: #fff8fc;
    border: 1px solid var(--line);
    border-radius: 50%;
}

.bridge span {
    animation: heartbeat 2.4s ease-in-out infinite;
    font-size: 1.45rem;
}

/* --------------------------------------------------------------------------
   CÂU TRÍCH VÀ BỘ ĐẾM
--------------------------------------------------------------------------- */

.quote {
    text-align: center;
    color: var(--muted);
    font-style: italic;
    line-height: 1.9;
    font-size: .92rem;

    margin: 0 auto;
    max-width: 640px;
    padding: 0 14px;
}

.counter {
    position: relative;
    overflow: hidden;

    text-align: center;
    padding: 26px 20px;

    border: 1px solid var(--line);
    border-radius: 26px;
    background: linear-gradient(120deg, #fffaf2, #fff0f6 55%, #f5efff);

    transform-style: preserve-3d;
    will-change: transform;
    transition: transform .18s ease;
}

.counter::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;

    background: linear-gradient(
        110deg,
        transparent 30%,
        #ffffffb3 50%,
        transparent 70%
    );

    animation: shimmer 9s ease-in-out infinite;
}

.days {
    color: var(--rose);
    font-size: 4.8rem;
    line-height: 1.15;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    margin: 8px 0;

    transform: translateZ(30px);
}

.day-label {
    font-family: "Great Vibes", cursive;
    font-size: 2rem;
    color: var(--rose);
}

.date {
    font-size: .78rem;
    color: var(--muted);
    margin: 12px 0 0;
}

/* --------------------------------------------------------------------------
   GẤU BÔNG
--------------------------------------------------------------------------- */

.section-head {
    text-align: center;
    margin: 0 0 18px;
}

.section-head h2 {
    font-size: 1.4rem;
    color: var(--rose);
    margin: 0 0 6px;
}

.section-head p {
    color: var(--muted);
    font-size: .86rem;
    line-height: 1.7;
    margin: 0;
}

.bears {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

.bear {
    min-width: 0;

    display: grid;
    grid-template-rows: 60px 24px 40px;
    align-items: center;
    gap: 6px;

    text-align: center;
    padding: 18px 10px;

    border: 1px solid var(--line);
    border-radius: 22px;
    background: #ffffffc0;
    box-shadow: 0 8px 18px #9e476608;

    transform-style: preserve-3d;
    will-change: transform;
    transition: transform .15s ease, box-shadow .2s ease;
}

.bear:hover {
    box-shadow: 0 14px 24px #9e47661c;
}

.bear:active {
    transform: scale(.97);
}

.face {
    font-size: 2.8rem;
    transform: translateZ(25px);
}

.bear strong {
    font-size: .85rem;
}

.bear small {
    color: var(--muted);
    line-height: 1.6;
    font-size: .74rem;
}

.speech {
    text-align: center;
    line-height: 1.8;
    font-size: .9rem;

    padding: 16px 18px;
    min-height: 65px;
    margin: 16px 0 0;

    border: 1px dashed #dfb6c8;
    border-radius: 18px;
    background: #ffffff70;
    color: var(--rose);
}

/* --------------------------------------------------------------------------
   FORM VIẾT THƯ
--------------------------------------------------------------------------- */

.form-panel {
    border: 1px solid var(--line);
    border-radius: 26px;
    padding: 24px;
    background: #ffffffb8;
    box-shadow: 0 12px 28px #9e476608;
}

label {
    display: block;
    font-size: .87rem;
    font-weight: 700;
    margin-bottom: 8px;
}

select,
textarea {
    width: 100%;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: #fffbfd;
    padding: 12px;
    color: var(--ink);
}

select {
    min-height: 46px;
    margin-bottom: 16px;
}

textarea {
    min-height: 122px;
    resize: vertical;
    line-height: 1.75;
}

.form-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-top: 14px;
}

.char-count {
    font-size: .74rem;
    color: var(--muted);
}

.send {
    padding: 12px 24px;
    min-height: 46px;

    border: 0;
    border-radius: 13px;
    background: linear-gradient(110deg, #b14a6d, #d47a98);
    color: white;
    font-weight: 700;

    box-shadow: 0 6px 18px #b14a6d20;
}

.send:hover {
    filter: brightness(1.06);
}

.status {
    font-size: .82rem;
    line-height: 1.6;
    color: var(--rose);
    margin: 12px 0 0;
}

.status:empty {
    display: none;
}

.privacy {
    font-size: .73rem;
    color: var(--muted);
    line-height: 1.7;
    margin: 12px 0 0;
}

/* --------------------------------------------------------------------------
   NHẬT KÝ — CHỈ HIỂN THỊ MỘT LỜI TẠI MỘT THỜI ĐIỂM
--------------------------------------------------------------------------- */

.letter {
    padding: 24px;
    border: 1px solid var(--line);
    border-radius: 22px;
    background: linear-gradient(140deg, #fffdf8, #fff2f8);

    opacity: 1;
    transform: translateY(0);
    transition: opacity 1s ease, transform 1s ease;
}

.letter.faded {
    opacity: 0;
    transform: translateY(7px);
}

.letter-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
}

.who {
    font-weight: 800;
    color: var(--rose);
}

.when {
    font-size: .76rem;
    color: var(--muted);
}

.letter-body {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.85;
    margin: 14px 0 0;
    font-size: .94rem;
}

.diary-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 14px;
    color: var(--muted);
    font-size: .78rem;
}

.small-button {
    border: 1px solid var(--line);
    background: #fff9fc;
    border-radius: 99px;
    padding: 8px 14px;
    min-height: 38px;
}

details {
    margin-top: 16px;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px 18px;
    background: #ffffff70;
}

summary {
    cursor: pointer;
    font-size: .85rem;
    color: var(--rose);
}

.archive-letter {
    padding: 18px 0;
    border-bottom: 1px solid var(--line);
}

.archive-letter:last-child {
    border-bottom: 0;
}

.empty {
    text-align: center;
    padding: 24px;
    line-height: 1.8;
    color: var(--muted);
    border: 1px dashed var(--line);
    border-radius: 20px;
    font-size: .9rem;
}

footer {
    text-align: center;
    font-size: .74rem;
    color: var(--muted);
    padding: 0 0 4px;
}

/* --------------------------------------------------------------------------
   HIỆU ỨNG KHI CHẠM
--------------------------------------------------------------------------- */

.particle {
    position: fixed;
    pointer-events: none;
    z-index: 20;
    animation: fly 1.6s ease-out forwards;
}

.wiggle {
    animation: wiggle .6s ease;
}

@keyframes twinkle {
    0%, 100% {
        opacity: .15;
        transform: scale(.6) rotate(0);
    }
    50% {
        opacity: .8;
        transform: scale(1.15) rotate(30deg);
    }
}

@keyframes cardEntrance {
    0% {
        opacity: 0;
        transform: perspective(1200px) rotateX(-18deg) translateY(42px) scale(.94);
        filter: blur(8px);
    }
    58% {
        opacity: 1;
        transform: perspective(1200px) rotateX(3deg) translateY(-5px) scale(1.01);
        filter: blur(0);
    }
    100% {
        opacity: 1;
        transform: perspective(1200px) rotateX(0) translateY(0) scale(1);
        filter: blur(0);
    }
}

@keyframes drift {
    to {
        transform: translate(60px, 100px);
    }
}

@keyframes heartbeat {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.17);
    }
}

@keyframes shimmer {
    0%, 55% {
        transform: translateX(-150%);
    }
    85%, 100% {
        transform: translateX(150%);
    }
}

@keyframes equalize {
    to {
        height: 15px;
    }
}

@keyframes fly {
    from {
        opacity: 1;
        transform: translate(-50%, -50%) scale(.5);
    }
    to {
        opacity: 0;
        transform:
            translate(var(--dx), -135px)
            rotate(var(--turn))
            scale(1.2);
    }
}

@keyframes wiggle {
    0%, 100% {
        transform: rotate(0);
    }
    30% {
        transform: rotate(-12deg);
    }
    65% {
        transform: rotate(10deg);
    }
}

@keyframes charmFloat {
    0%, 100% {
        transform: translateY(0) rotate(-9deg);
        opacity: .40;
    }
    50% {
        transform: translateY(-17px) rotate(9deg);
        opacity: .65;
    }
}

@keyframes charmGlint {
    0%, 100% {
        opacity: .18;
        transform: scale(.65) rotate(0);
    }
    50% {
        opacity: .85;
        transform: scale(1.15) rotate(35deg);
    }
}

@keyframes fairyGlow {
    0%, 100% {
        opacity: .15;
        transform: translateY(0) scale(.6);
    }
    50% {
        opacity: .85;
        transform: translateY(-10px) scale(1.15);
    }
}

/* --------------------------------------------------------------------------
   HIỆU ỨNG BỔ SUNG: TRÁI TIM BAY, SAO BĂNG, HIỆN DẦN
--------------------------------------------------------------------------- */

/* Các lớp nền là khối tuyệt đối phủ toàn bộ, để parallax dịch được cả lớp */
#stars, #charms, #lights, #floaters {
    position: absolute;
    inset: 0;
}

.floater {
    position: absolute;
    bottom: -40px;
    pointer-events: none;
    opacity: 0;
    filter: drop-shadow(0 4px 10px rgba(236, 151, 188, .35));
    animation: rise var(--duration) linear forwards;
}

@keyframes rise {
    0% {
        transform: translateY(0) translateX(0) rotate(-8deg);
        opacity: 0;
    }
    10% {
        opacity: .7;
    }
    50% {
        transform: translateY(-55vh) translateX(var(--sway)) rotate(8deg);
    }
    90% {
        opacity: .5;
    }
    100% {
        transform: translateY(-112vh) translateX(calc(var(--sway) * -0.6)) rotate(-6deg);
        opacity: 0;
    }
}

.shooting-star {
    position: absolute;
    width: 130px;
    height: 2px;
    background: linear-gradient(90deg, rgba(255, 255, 255, .95), transparent);
    border-radius: 2px;
    transform: rotate(-35deg);
    opacity: 0;
    animation: shoot 9s ease-in infinite;
    animation-delay: var(--delay);
}

.shooting-star::after {
    content: "";
    position: absolute;
    right: 0;
    top: -2px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 0 12px 4px rgba(255, 220, 240, .8);
}

@keyframes shoot {
    0%, 88% {
        opacity: 0;
        transform: translate(0, 0) rotate(-35deg);
    }
    91% {
        opacity: 1;
    }
    100% {
        opacity: 0;
        transform: translate(-62vw, 42vh) rotate(-35deg);
    }
}

@keyframes titleShimmer {
    to {
        background-position: 300% 0;
    }
}

.reveal {
    opacity: 0;
    transform: translateY(26px);
    transition: opacity .8s ease, transform .8s ease;
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

#stars, #charms, #lights, #floaters, .orb {
    will-change: translate;
}

/* --------------------------------------------------------------------------
   ĐIỆN THOẠI
--------------------------------------------------------------------------- */

@media (max-width: 600px) {
    body {
        padding: 8px 4px 20px;
    }

    main {
        gap: 22px;
    }

    .hero {
        padding-top: 12px;
    }

    .profiles {
        gap: 12px;
    }

    .profile {
        padding: 20px 14px 16px;
        grid-template-rows: 80px 84px 46px 1fr auto;
        border-radius: 22px;
    }

    .profile h2 {
        font-size: 2rem;
    }

    .role {
        font-size: .67rem;
    }

    .details {
        grid-template-columns: 1fr;
        gap: 2px;
        min-height: 176px;
        font-size: .82rem;
    }

    .details dd {
        margin-bottom: 9px;
    }

    .mood-text {
        min-height: 90px;
        font-size: .78rem;
    }

    .mood {
        font-size: .76rem;
        padding: 8px;
    }

    .bridge {
        width: 32px;
        height: 32px;
        top: 44%;
    }

    .bridge span {
        font-size: 1.1rem;
    }

    .bears {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .form-panel {
        padding: 20px;
    }

    .section-head h2 {
        font-size: 1.25rem;
    }

    .form-bottom {
        align-items: stretch;
        flex-direction: column;
    }

    .send {
        width: 100%;
    }

    .charm-icon {
        font-size: calc(var(--size) * .75);
    }

    .charm:nth-of-type(3n) {
        display: none;
    }
}

@media (max-width: 350px) {
    .profiles {
        grid-template-columns: 1fr;
    }

    .bridge {
        display: none;
    }

    .profile {
        grid-template-rows: 80px 70px 30px 1fr auto;
    }

    .details {
        min-height: 0;
    }

    .mood-text {
        min-height: 50px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation: none !important;
        transition: none !important;
    }

    .particle {
        display: none;
    }

    .star {
        opacity: .25;
    }
}
</style>
</head>

<body>
<main id="scene">

    <div class="ambient" aria-hidden="true">
        <div class="orb"></div>
        <div class="orb two"></div>
        <div id="stars"></div>
        <div id="charms"></div>
        <div id="lights"></div>
        <div id="floaters"></div>
        <span class="shooting-star" style="top: 18%; left: 80%; --delay: 0s;"></span>
        <span class="shooting-star" style="top: 38%; left: 55%; --delay: 4.5s;"></span>
    </div>

    <header class="hero">
        <div class="eyebrow">
            MỘT CHÚT DUYÊN · MỘT ĐỜI THƯƠNG
        </div>

        <h1>Chuyện tình chúng mình</h1>

        <p class="subtitle">
            Giữa thế giới rộng lớn, thật may vì có nhau.
        </p>

        <button
            id="music"
            class="music"
            type="button"
            disabled
            aria-pressed="false"
        >
            <span class="equalizer" aria-hidden="true">
                <i></i><i></i><i></i>
            </span>
            <span id="music-label">
                Đang tải bản nhạc của chúng mình…
            </span>
        </button>

        <p id="music-note" class="music-note">
            Một chút nhạc, một chút thương.
        </p>

        <div class="audio-frame">
            <iframe
                id="sc-player"
                title="Nhạc tình yêu"
                allow="autoplay"
                tabindex="-1"
            ></iframe>
        </div>
    </header>

    <section class="profiles" aria-label="Hai người thương">
        <article class="profile">
            <div class="avatar">🐶</div>

            <h2>Tạ Vũ Lương</h2>

            <p class="role">CHÀNG TRAI CỦA TÔI</p>

            <dl class="details">
                <dt>Tên gọi</dt>
                <dd>Anh Yêu 💙</dd>

                <dt>Sở thích</dt>
                <dd>Yêu em, che chở cho em, tặng hoa mỗi ngày.</dd>
            </dl>

            <div>
                <button
                    class="mood"
                    data-person="luong"
                    type="button"
                >
                    🐶 Tâm trạng hôm nay
                </button>

                <p
                    class="mood-text"
                    id="mood-luong"
                    aria-live="polite"
                >
                    Chạm nhẹ để nghe anh thì thầm…
                </p>
            </div>
        </article>

        <div class="bridge" aria-hidden="true">
            <span>💗</span>
        </div>

        <article class="profile">
            <div class="avatar">🍅</div>

            <h2>Hoàng Thị Thùy Dương</h2>

            <p class="role">CÔ GÁI NHỎ DỊU DÀNG</p>

            <dl class="details">
                <dt>Tên gọi</dt>
                <dd>Cà Chua 💗</dd>

                <dt>Sở thích</dt>
                <dd>Được chiều chuộng, thích hoa hồng và trái tim.</dd>
            </dl>

            <div>
                <button
                    class="mood"
                    data-person="duong"
                    type="button"
                >
                    🍅 Tâm trạng hôm nay
                </button>

                <p
                    class="mood-text"
                    id="mood-duong"
                    aria-live="polite"
                >
                    Chạm nhẹ để nghe em kể chuyện…
                </p>
            </div>
        </article>
    </section>

    <p class="quote">
        “Cảm ơn vì giữa hàng tỷ người, chúng ta đã tìm thấy<br>
        và chọn đồng hành cùng nhau.”
    </p>

    <section class="counter" aria-label="Ngày bên nhau">
        <div class="eyebrow">TỪ NGÀY MÌNH CÓ NHAU</div>
        <div class="days" id="days">0</div>
        <div class="day-label">Ngày thương, ngày nhớ!</div>
        <p class="date">
            10.09.2026 · Và còn thật nhiều ngày sau nữa ♡
        </p>
    </section>

    <section id="bear-section">
        <div class="section-head">
            <h2>Bốn chiếc gấu, một trời thương</h2>
            <p>Chạm vào một bạn gấu để nhận điều dịu dàng.</p>
        </div>

        <div class="bears">
            <button type="button" class="bear" data-kind="kiss">
                <span class="face">🧸</span>
                <strong>Gấu Nụ Hôn</strong>
                <small>Một ngàn chiếc hôn</small>
            </button>

            <button type="button" class="bear" data-kind="hug">
                <span class="face">🐻</span>
                <strong>Gấu Ôm Ấm</strong>
                <small>Một vòng tay thật lâu</small>
            </button>

            <button type="button" class="bear" data-kind="rose">
                <span class="face">🐻‍❄️</span>
                <strong>Gấu Tặng Hoa</strong>
                <small>Một bó hoa dành riêng</small>
            </button>

            <button type="button" class="bear" data-kind="luck">
                <span class="face">🧸</span>
                <strong>Gấu Bói Tình</strong>
                <small>Một lời hẹn ngày mai</small>
            </button>
        </div>

        <p class="speech" id="speech" aria-live="polite">
            Có những ngày, chỉ một chút yêu thương
            cũng đủ làm lòng ấm lại. ♡
        </p>
    </section>

    <section id="compose">
        <div class="section-head">
            <h2>💌 Một lá thư gửi người thương</h2>
            <p>
                Có những điều viết ra sẽ dịu dàng hơn một lời nói.
            </p>
        </div>

        <form id="letter-form" class="form-panel">
            <label for="sender">Hôm nay ai gửi thương?</label>

            <select id="sender">
                <option>🐶 Chú Chó Lương</option>
                <option>🍅 Cà Chua Dương</option>
            </select>

            <label for="message">Lời nhắn của bạn</label>

            <textarea
                id="message"
                required
                maxlength="3000"
                placeholder="Hôm nay anh/em muốn nói rằng…"
            ></textarea>

            <div class="form-bottom">
                <span class="char-count" id="char-count">
                    0 / 3000 ký tự
                </span>

                <button class="send" type="submit">
                    Gửi một chút thương ♡
                </button>
            </div>

            <p class="status" id="status" role="status"></p>

            <p class="privacy" id="privacy">
                Đang kiểm tra kết nối…
            </p>
        </form>
    </section>

    <section id="diary-section">
        <div class="section-head">
            <h2>Những lời thương còn ở lại</h2>
            <p>Mỗi lá thư là một điều dịu dàng được giữ lại.</p>
        </div>

        <div id="empty" class="empty">
            Một trang giấy còn trống.<br>
            Một người thương đang đợi lời đầu tiên của bạn. ♡
        </div>

        <div id="diary" hidden>
            <article class="letter" id="letter">
                <div class="letter-header">
                    <span class="who" id="who"></span>
                    <span class="when" id="when"></span>
                </div>

                <p class="letter-body" id="letter-body"></p>
            </article>

            <div class="diary-controls">
                <span id="position"></span>

                <button
                    class="small-button"
                    id="pause"
                    type="button"
                >
                    Tạm dừng
                </button>

                <button
                    class="small-button"
                    id="next"
                    type="button"
                >
                    Lời tiếp theo ♡
                </button>
            </div>

            <details id="archive">
                <summary>📖 Đọc toàn bộ lời nhắn</summary>
                <div id="archive-items"></div>
            </details>
        </div>
    </section>

    <footer>
        Dành riêng cho Lương & Dương · bằng tất cả dịu dàng
    </footer>

</main>

<script>
"use strict";

// ===========================================================================
// KẾT NỐI CHIỀU CAO VỚI STREAMLIT
// ===========================================================================

function sendToHost(type, data = {}) {
    if (window.parent !== window) {
        window.parent.postMessage(
            {
                isStreamlitMessage: true,
                type,
                ...data
            },
            "*"
        );
    }
}

let lastHeight = 0;

function fit() {
    const scene = document.getElementById("scene");
    const style = getComputedStyle(document.body);

    const height = Math.ceil(
        scene.getBoundingClientRect().height
        + parseFloat(style.paddingTop)
        + parseFloat(style.paddingBottom)
    );

    if (height !== lastHeight) {
        lastHeight = height;

        sendToHost(
            "streamlit:setFrameHeight",
            { height }
        );
    }
}

window.addEventListener("message", event => {
    if (
        event.source === window.parent
        && event.data?.type === "streamlit:render"
    ) {
        lastHeight = 0;
        fit();
    }
});

sendToHost(
    "streamlit:componentReady",
    { apiVersion: 1 }
);

new ResizeObserver(fit).observe(
    document.getElementById("scene")
);

window.addEventListener("resize", fit);
document.fonts.ready.then(fit);
fit();


// ===========================================================================
// TIỆN ÍCH
// ===========================================================================

const $ = id => document.getElementById(id);

const reduced = matchMedia(
    "(prefers-reduced-motion: reduce)"
);

const pick = items => (
    items[Math.floor(Math.random() * items.length)]
);


// ===========================================================================
// CẤU HÌNH (sửa ở đây cho dễ)
// ===========================================================================

// Ngày bắt đầu yêu nhau (năm, tháng 0-based, ngày).
const START_DATE = { year: 2026, month: 8, day: 10 };

// Link nhạc SoundCloud.
const TRACK = (
    "https://soundcloud.com/s-m-sung-s-t/"
    + "nhac-au-my-hay-nhat-moi-thoi-dai-"
    + "nhac-tieng-anh-nhe-nhang-sau-lang-thoang-buon-man-mac"
);

// ===========================================================================
// LƯU CHUNG TRÊN MÁY CHỦ STREAMLIT
// ===========================================================================
let messages = [];
let pendingLetter = null;
let messageSnapshot = "";

function sanitize(message) {
    return message && typeof message.sender === "string"
        && typeof message.text === "string" && typeof message.time === "string";
}

function requestSync() {
    sendToHost("streamlit:setComponentValue", {
        value: { request: Date.now(), letter: pendingLetter },
        dataType: "json"
    });
}

window.addEventListener("message", event => {
    if (event.source !== window.parent
        || event.data?.type !== "streamlit:render") return;
    const args = event.data.args || {};
    if (pendingLetter && args.ack === pendingLetter.id) {
        pendingLetter = null;
        $("message").value = "";
        $("char-count").textContent = "0 / 3000 ký tự";
        $("message").disabled = false;
        document.querySelector(".send").disabled = false;
        $("status").textContent = "Đã lưu lời thương. Người ấy sẽ thấy sau vài giây. 💗";
        burst(document.querySelector(".send"), ["💌", "💖", "✨"]);
    }
    if (args.error) {
        pendingLetter = null;
        $("message").disabled = false;
        document.querySelector(".send").disabled = false;
        $("status").textContent = args.error;
    }
    if (Array.isArray(args.messages)) {
        const snapshot = JSON.stringify(args.messages);
        if (snapshot !== messageSnapshot) {
            messageSnapshot = snapshot;
            messages = args.messages.filter(sanitize);
            refresh();
        }
    }
});
setInterval(() => {
    if (!document.hidden) requestSync();
}, 4000);
document.addEventListener("visibilitychange", () => {
    if (!document.hidden) requestSync();
});

// ===========================================================================
// BỘ ĐẾM NGÀY — THEO GIỜ VIỆT NAM
// ===========================================================================

function updateDays() {
    const parts = new Intl.DateTimeFormat(
        "en-CA",
        {
            timeZone: "Asia/Ho_Chi_Minh",
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        }
    ).formatToParts(new Date());

    const date = Object.fromEntries(
        parts.map(part => [part.type, part.value])
    );

    const today = Date.UTC(
        Number(date.year),
        Number(date.month) - 1,
        Number(date.day)
    );

    const start = Date.UTC(
        START_DATE.year,
        START_DATE.month,
        START_DATE.day
    );

    const days = Math.max(
        0,
        Math.floor((today - start) / 86400000)
    );

    $("days").textContent = days;
}

updateDays();
setInterval(updateDays, 60000);


// ===========================================================================
// NỀN CHARM: NƠ, HOA, TRÁI TIM VÀ BỤI ÁNH SÁNG
// ===========================================================================

const starLayer = $("stars");
const charmLayer = $("charms");
const lightLayer = $("lights");
const floaterLayer = $("floaters");

starLayer.replaceChildren();
charmLayer.replaceChildren();
lightLayer.replaceChildren();

// Bố trí có chủ ý để charm phân bố đều.
const charms = [
    { icon: "🎀", x: 7,  y: 5,  size: 31 },
    { icon: "🌸", x: 92, y: 8,  size: 32 },
    { icon: "🤍", x: 24, y: 12, size: 25 },
    { icon: "💗", x: 77, y: 15, size: 25 },

    { icon: "🧸", x: 4,  y: 25, size: 31 },
    { icon: "🫧", x: 96, y: 29, size: 32 },
    { icon: "🎀", x: 49, y: 35, size: 26 },

    { icon: "🌷", x: 8,  y: 42, size: 31 },
    { icon: "💖", x: 91, y: 46, size: 29 },
    { icon: "🌸", x: 35, y: 49, size: 24 },

    { icon: "🤍", x: 5,  y: 58, size: 27 },
    { icon: "🎀", x: 95, y: 63, size: 32 },
    { icon: "🧸", x: 53, y: 67, size: 26 },

    { icon: "🫧", x: 8,  y: 76, size: 32 },
    { icon: "🌸", x: 92, y: 80, size: 30 },
    { icon: "💗", x: 28, y: 87, size: 27 },

    { icon: "🎀", x: 73, y: 93, size: 29 },
    { icon: "🤍", x: 10, y: 97, size: 25 }
];

charms.forEach((item, index) => {
    const charm = document.createElement("span");
    charm.className = "charm";
    charm.setAttribute("aria-hidden", "true");

    charm.style.left = `${item.x}%`;
    charm.style.top = `${item.y}%`;
    charm.style.setProperty("--size", `${item.size}px`);
    charm.style.setProperty(
        "--duration",
        `${6 + (index % 5)}s`
    );
    charm.style.setProperty(
        "--delay",
        `${-(index * 1.3)}s`
    );

    const icon = document.createElement("span");
    icon.className = "charm-icon";
    icon.textContent = item.icon;

    charm.appendChild(icon);
    charmLayer.appendChild(charm);
});

// Sao: chia nền thành các vùng để phân bố đều.
for (let i = 0; i < 40; i++) {
    const star = document.createElement("span");

    const column = i % 5;
    const row = Math.floor(i / 5);

    star.className = "star";
    star.textContent = i % 3 === 0 ? "✧" : "✦";
    star.setAttribute("aria-hidden", "true");

    star.style.left = (
        `${column * 20 + 3 + Math.random() * 12}%`
    );

    star.style.top = (
        `${row * 12.5 + 2 + Math.random() * 8}%`
    );

    star.style.fontSize = `${9 + Math.random() * 10}px`;
    star.style.setProperty(
        "--speed",
        `${3 + Math.random() * 4}s`
    );
    star.style.setProperty(
        "--delay",
        `${-Math.random() * 8}s`
    );

    starLayer.appendChild(star);
}

// Chấm sáng nhỏ như bụi kim tuyến.
for (let i = 0; i < 24; i++) {
    const light = document.createElement("span");

    light.className = "fairy-light";
    light.setAttribute("aria-hidden", "true");

    light.style.left = `${3 + Math.random() * 94}%`;
    light.style.top = `${2 + Math.random() * 96}%`;

    light.style.setProperty(
        "--size",
        `${2 + Math.random() * 3}px`
    );
    light.style.setProperty(
        "--duration",
        `${4 + Math.random() * 5}s`
    );
    light.style.setProperty(
        "--delay",
        `${-Math.random() * 9}s`
    );

    lightLayer.appendChild(light);
}


// ===========================================================================
// HIỆU ỨNG 3D: NGHIÊNG THEO CHUỘT
// ===========================================================================

function enableTilt(element, maxDeg = 7) {
    if (reduced.matches) return;

    element.addEventListener("mousemove", event => {
        const rect = element.getBoundingClientRect();

        const px = (event.clientX - rect.left) / rect.width - 0.5;
        const py = (event.clientY - rect.top) / rect.height - 0.5;

        element.style.transform = (
            `perspective(900px) `
            + `rotateX(${(-py * maxDeg).toFixed(2)}deg) `
            + `rotateY(${(px * maxDeg).toFixed(2)}deg) `
            + `translateZ(0)`
        );
    });

    element.addEventListener("mouseleave", () => {
        element.style.transform = "";
    });
}

document.querySelectorAll(".profile").forEach(el => {
    enableTilt(el, 8);
});

document.querySelectorAll(".bear").forEach(el => {
    enableTilt(el, 10);
});

enableTilt($("days").closest(".counter"), 4);


// ===========================================================================
// PARALLAX 3D: CÁC LỚP NỀN CHUYỂN ĐỘNG NHẸ THEO CHUỘT
// ===========================================================================

let targetX = 0, targetY = 0;
let curX = 0, curY = 0;

const parallaxLayers = [
    { el: document.querySelector(".orb"), depth: 26 },
    { el: document.querySelector(".orb.two"), depth: -20 },
    { el: charmLayer, depth: 14 },
    { el: lightLayer, depth: 9 },
    { el: starLayer, depth: 5 },
    { el: floaterLayer, depth: 11 },
];

window.addEventListener("mousemove", event => {
    targetX = (event.clientX / window.innerWidth - 0.5) * 2;
    targetY = (event.clientY / window.innerHeight - 0.5) * 2;
});

function parallaxLoop() {
    curX += (targetX - curX) * 0.06;
    curY += (targetY - curY) * 0.06;

    for (const layer of parallaxLayers) {
        if (!layer.el) continue;
        layer.el.style.translate =
            `${(curX * layer.depth).toFixed(2)}px ${(curY * layer.depth).toFixed(2)}px`;
    }

    requestAnimationFrame(parallaxLoop);
}

if (!reduced.matches) {
    parallaxLoop();
}


// ===========================================================================
// TRÁI TIM BAY LÊN (LẤP ĐẦY KHOẢNG TRỐNG)
// ===========================================================================

const FLOATER_EMOJIS = ["💗", "🩷", "💕", "🌸", "🫧", "💖", "✨", "🤍"];

function spawnFloater() {
    if (reduced.matches) return;
    if (floaterLayer.childElementCount > 16) return;

    const el = document.createElement("span");
    el.className = "floater";
    el.textContent = pick(FLOATER_EMOJIS);

    const size = 14 + Math.random() * 20;
    const left = Math.random() * 100;
    const duration = 9 + Math.random() * 8;
    const sway = 20 + Math.random() * 40;

    el.style.left = `${left}%`;
    el.style.fontSize = `${size}px`;
    el.style.setProperty("--duration", `${duration}s`);
    el.style.setProperty("--sway", `${sway}px`);

    floaterLayer.appendChild(el);

    el.addEventListener("animationend", () => el.remove());
}

spawnFloater();
setInterval(spawnFloater, 1300);


// ===========================================================================
// HIỆN DẦN KHI CUỘN
// ===========================================================================

const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

[
    ".quote",
    "#bear-section",
    "#compose",
    "#diary-section",
    "footer"
].forEach(selector => {
    const el = document.querySelector(selector);
    if (el) {
        el.classList.add("reveal");
        revealObserver.observe(el);
    }
});


// ===========================================================================
// TRÁI TIM VÀ ÁNH SAO BAY KHI CHẠM
// ===========================================================================

function burst(
    element,
    symbols = ["✨", "💗", "✦"]
) {
    if (reduced.matches) return;

    // Không tạo quá nhiều hạt khi bấm liên tục.
    if (
        document.querySelectorAll(".particle").length > 60
    ) {
        return;
    }

    const rect = element.getBoundingClientRect();

    for (let i = 0; i < 12; i++) {
        const particle = document.createElement("span");

        particle.className = "particle";
        particle.setAttribute("aria-hidden", "true");
        particle.textContent = pick(symbols);

        particle.style.cssText = `
            left: ${rect.left + rect.width / 2}px;
            top: ${rect.top + rect.height / 2}px;
            font-size: ${14 + Math.random() * 12}px;
            --dx: ${Math.random() * 180 - 90}px;
            --turn: ${Math.random() * 50 - 25}deg;
        `;

        document.body.appendChild(particle);

        setTimeout(
            () => particle.remove(),
            1700
        );
    }
}


// ===========================================================================
// TÂM TRẠNG
// ===========================================================================

const moods = {
    luong: [
        "🥰 Đang nhớ Cà Chua muốn xỉu luôn nè.",
        "😋 Hơi đói bụng, nhưng nhớ em nhiều hơn đói.",
        "😴 Buồn ngủ nhưng vẫn muốn nghe em kể chuyện.",
        "🥺 Mong tan làm sớm để gọi video cho em.",
        "💗 Chỉ cần thấy tin nhắn của em là ngày dài bỗng dịu lại.",
        "🌤️ Hôm nay vui lắm, muốn kể Cà Chua nghe đầu tiên.",
        "🤭 Đang cười một mình vì nhớ lại chuyện hai đứa.",
        "🫶 Muốn ôm em thật lâu, chẳng cần nói gì cả.",
        "🐶 Chú Chó Lương hôm nay ngoan, chỉ hơi nhớ em quá thôi.",
        "☕ Ước gì lúc này được ngồi cạnh em và uống gì đó thật ấm.",
        "✨ Nghĩ đến tương lai của hai đứa là tự nhiên thấy háo hức.",
        "🌙 Tối nay nhớ ngủ sớm nhé, anh vẫn luôn thương em.",
        "💌 Có một điều muốn nói mãi: cảm ơn em đã xuất hiện.",
        "🌷 Hôm nay bình thường, nhưng nghĩ đến em là thành ngày đẹp.",
        "😚 Đang có sẵn một chiếc hôn, chờ gặp em để gửi tận nơi.",
        "🏡 Chỉ mong sớm đến ngày những điều nhỏ bé đều có em bên cạnh.",
        "🌦️ Dù hôm nay có hơi mệt, nghĩ đến em là anh lại có động lực.",
        "🎧 Đang nghe một bài hát và thấy câu nào cũng giống chuyện mình.",
        "🍀 Anh thấy mình thật may mắn vì giữa bao người lại gặp được em.",
        "🛵 Muốn chạy đến gặp em ngay, chỉ để nhìn em cười một chút.",
        "🧸 Nhớ em kiểu mềm mềm, ấm ấm như ôm một chú gấu bông.",
        "💭 Đầu anh hôm nay có rất nhiều việc, nhưng em vẫn ở vị trí đầu tiên.",
        "🌅 Mong ngày mai thức dậy sẽ nhận được lời chào buổi sáng của em.",
        "💕 Anh vẫn đang thương em nhiều hơn một chút so với ngày hôm qua."
    ],

    duong: [
        "🥰 Đang cười tủm tỉm vì nghĩ đến chú Chó Lương.",
        "😋 Thèm ăn vặt, ước gì có ai đó mua cho.",
        "🙈 Ngại ghê, nhưng thật ra rất nhớ anh.",
        "😌 Bình yên vì biết có người luôn thương mình.",
        "💗 Chỉ cần anh hỏi một câu thôi là mọi mệt mỏi nhẹ đi rồi.",
        "🌸 Hôm nay tâm trạng xinh như hoa vì có anh trong lòng.",
        "🤭 Đang nhớ một người hay làm em vừa giận vừa thương.",
        "🫂 Muốn được anh ôm một cái thật chặt ngay bây giờ.",
        "🍅 Cà Chua hôm nay đỏ mặt vì lại nghĩ đến anh đó.",
        "☕ Muốn cùng anh trốn cả thế giới, ngồi cạnh nhau thật lâu.",
        "✨ Nghĩ đến những chuyến đi sau này của hai đứa là thấy vui.",
        "🌙 Chúc chú Chó Lương một tối thật ngoan và ngủ thật ngon.",
        "💌 Em có rất nhiều chuyện nhỏ xíu chỉ muốn kể riêng anh nghe.",
        "🌷 Một ngày có anh quan tâm luôn là một ngày dịu dàng.",
        "😚 Đang để dành một chiếc hôn thật lâu cho lần gặp tới.",
        "🏡 Mong sau này ngày nào thức dậy cũng thấy anh ở bên.",
        "🌦️ Hôm nay có hơi mệt một chút, muốn nghe giọng anh để nạp pin.",
        "🎧 Bài hát đang nghe làm em nhớ đến những khoảnh khắc của hai đứa.",
        "🍀 Em thấy thật may vì đã gặp một người luôn dịu dàng với mình.",
        "🛵 Muốn anh xuất hiện trước mặt ngay để mình cùng đi ăn gì đó.",
        "🧸 Hôm nay chỉ muốn làm em bé, được anh dỗ dành và ôm thật lâu.",
        "💭 Dù đang bận, trong đầu em vẫn có một góc nhỏ dành riêng cho anh.",
        "🌅 Mong sáng mai vừa mở mắt đã thấy tin nhắn của chú Chó Lương.",
        "💕 Hình như hôm nay em lại thương anh nhiều hơn hôm qua rồi."
    ]
};

// Nhớ câu vừa hiện để không lặp liên tiếp.
const lastMood = { luong: -1, duong: -1 };

function nextMood(person) {
    const list = moods[person];

    let index = Math.floor(Math.random() * list.length);
    if (index === lastMood[person]) {
        index = (index + 1) % list.length;
    }

    lastMood[person] = index;
    return list[index];
}

document.querySelectorAll(".mood").forEach(button => {
    button.addEventListener("click", () => {
        const person = button.dataset.person;

        $("mood-" + person).textContent = nextMood(person);

        burst(button);
    });
});


// ===========================================================================
// GẤU BÔNG
// ===========================================================================

const lines = {
    kiss: [
        "💋 Đã gửi 1000 nụ hôn ngọt ngào đến Cà Chua!",
        "😘 Hôn thêm 500 cái nữa cho đủ ngọt nhé!",
        "💝 Gấu vừa giấu một nụ hôn trong túi áo Anh Yêu rồi."
    ],

    hug: [
        "🤗 Gửi Chú Chó Lương một chiếc ôm thật ấm!",
        "🫂 Ôm lâu thêm 10 giây nữa, đừng buông vội.",
        "🐶 Chú Chó vẫy đuôi mừng rỡ vì được ôm!"
    ],

    rose: [
        "🌹 Một bó hồng tưởng tượng, kèm thật nhiều thương.",
        "💐 Hoa hôm nay thơm hơn vì có tên em trên thiệp.",
        "🌷 Nếu nỗi nhớ nở thành hoa, anh đã có cả khu vườn."
    ],

    luck: [
        "🔮 Gấu đoán hôm nay hai đứa sẽ cười với nhau thật nhiều.",
        "✨ Điều ước tối nay: được nắm tay nhau đi dạo.",
        "💫 Còn rất nhiều ngày hạnh phúc đang chờ chúng mình."
    ]
};

document.querySelectorAll(".bear").forEach(button => {
    button.addEventListener("click", () => {
        const kind = button.dataset.kind;

        $("speech").textContent = pick(lines[kind]);

        const face = button.querySelector(".face");

        face.classList.remove("wiggle");
        void face.offsetWidth;
        face.classList.add("wiggle");

        const symbols = kind === "rose"
            ? ["🌸", "🌹", "✨"]
            : ["💗", "✨", "💕"];

        burst(button, symbols);
    });
});


// ===========================================================================
// NHẬT KÝ
//
// Nội dung người dùng luôn được gán bằng textContent.
// ===========================================================================

let current = 0;
let timer = null;
let paused = reduced.matches;

function drawLetter() {
    if (!messages.length) return;

    const message = messages[current];

    $("who").textContent = message.sender;
    $("when").textContent = message.time;
    $("letter-body").textContent = message.text;

    $("position").textContent = (
        `Lời thương ${current + 1} / ${messages.length}`
    );

    $("letter").classList.remove("faded");
    fit();
}

function schedule() {
    clearTimeout(timer);

    if (
        paused
        || !messages.length
        || document.hidden
    ) {
        return;
    }

    // Lời dài được giữ lâu hơn.
    const hold = Math.max(
        6000,
        Math.min(
            24000,
            messages[current].text.length * 70
        )
    );

    timer = setTimeout(nextLetter, hold);
}

function nextLetter() {
    if (!messages.length) return;

    clearTimeout(timer);

    $("letter").classList.add("faded");

    timer = setTimeout(() => {
        current = (current + 1) % messages.length;

        drawLetter();
        schedule();
    }, reduced.matches ? 0 : 1050);
}

function buildArchive() {
    const box = $("archive-items");

    box.replaceChildren();

    messages.forEach(message => {
        const article = document.createElement("article");
        article.className = "archive-letter";

        const header = document.createElement("div");
        header.className = "letter-header";

        const who = document.createElement("span");
        who.className = "who";
        who.textContent = message.sender;

        const when = document.createElement("span");
        when.className = "when";
        when.textContent = message.time;

        const body = document.createElement("p");
        body.className = "letter-body";
        body.textContent = message.text;

        header.append(who, when);
        article.append(header, body);
        box.appendChild(article);
    });
}

function refresh() {
    clearTimeout(timer);

    current = 0;

    $("empty").hidden = messages.length > 0;
    $("diary").hidden = !messages.length;

    if (messages.length) {
        drawLetter();
        buildArchive();
        schedule();
    }

    fit();
}

function updatePrivacyNote() {
    $("privacy").textContent = "Lời nhắn lưu chung trên máy chủ Streamlit, cập nhật mỗi 4 giây. Dữ liệu có thể mất khi ứng dụng được khởi động hoặc triển khai lại.";
}

$("pause").textContent = (
    paused ? "Tiếp tục" : "Tạm dừng"
);

$("pause").addEventListener("click", () => {
    paused = !paused;

    clearTimeout(timer);
    drawLetter();

    $("pause").textContent = (
        paused ? "Tiếp tục" : "Tạm dừng"
    );

    schedule();
});

$("next").addEventListener("click", nextLetter);

document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);

    if (!document.hidden) {
        drawLetter();
        schedule();
    }
});

$("message").addEventListener("input", () => {
    $("char-count").textContent = (
        `${$("message").value.length} / 3000 ký tự`
    );

    $("message").setCustomValidity("");
});

$("letter-form").addEventListener("submit", event => {
    event.preventDefault();

    const text = $("message").value.trim();

    if (!text) {
        $("message").setCustomValidity(
            "Bạn viết vài dòng trước khi gửi nhé."
        );

        $("message").reportValidity();
        return;
    }

    const message = {
        sender: $("sender").value,
        text,
        time: new Intl.DateTimeFormat(
            "vi-VN",
            {
                timeZone: "Asia/Ho_Chi_Minh",
                dateStyle: "short",
                timeStyle: "short"
            }
        ).format(new Date())
    };

    if (pendingLetter) return;
    pendingLetter = {
        ...message,
        id: crypto.randomUUID()
    };
    $("message").disabled = true;
    document.querySelector(".send").disabled = true;
    $("status").textContent = "Đang lưu lời thương…";
    requestSync();
});

updatePrivacyNote();
refresh();


// ===========================================================================
// NHẠC SOUNDCLOUD
//
// - Yêu cầu tự phát khi mở trang.
// - Chỉ báo đang phát khi nhận sự kiện PLAY.
// - Tương tác trong trang không khiến Streamlit chạy lại.
// - Ghi nhớ vị trí bài nhạc.
// ===========================================================================

const MUSIC = "love_story_luong_duong_position_v3";

let widget = null;
let ready = false;
let playing = false;
let explicitPause = false;
let resume = 0;
let lastSave = 0;

try {
    resume = Number(localStorage.getItem(MUSIC)) || 0;
} catch (_) {
    resume = 0;
}

$("sc-player").src = (
    "https://w.soundcloud.com/player/?url="
    + encodeURIComponent(TRACK)
    + "&auto_play=true"
    + "&hide_related=true"
    + "&show_comments=false"
    + "&show_user=false"
    + "&visual=false"
);

function paintMusic(on) {
    playing = on;

    $("music").classList.toggle("playing", on);

    $("music").setAttribute(
        "aria-pressed",
        String(on)
    );

    $("music-label").textContent = on
        ? "Nhạc đang phát · chạm để tạm dừng"
        : "♫ Chạm để bật nhạc tình yêu";

    $("music-note").textContent = on
        ? "Cứ để bản nhạc kể tiếp chuyện chúng mình."
        : (
            "Nếu trình duyệt chặn tự phát, "
            + "chạm nút nhạc một lần nhé."
        );
}

function musicError() {
    $("music").disabled = true;

    $("music-label").textContent = (
        "Chưa tải được bản nhạc"
    );

    $("music-note").replaceChildren();

    const link = document.createElement("a");

    link.href = TRACK;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Mở bản nhạc trên SoundCloud";

    $("music-note").appendChild(link);
}

const loadTimer = setTimeout(() => {
    if (!ready) musicError();
}, 18000);

const api = document.createElement("script");

api.src = "https://w.soundcloud.com/player/api.js";
api.onerror = musicError;

api.onload = () => {
    if (!window.SC) {
        musicError();
        return;
    }

    widget = SC.Widget($("sc-player"));

    widget.bind(SC.Widget.Events.READY, () => {
        ready = true;

        clearTimeout(loadTimer);
        $("music").disabled = false;

        widget.setVolume(45);

        if (Number.isFinite(resume) && resume > 0) {
            widget.seekTo(resume);
        }

        widget.play();

        setTimeout(() => {
            widget.isPaused(isPaused => {
                paintMusic(!isPaused);
            });
        }, 1400);
    });

    widget.bind(SC.Widget.Events.PLAY, () => {
        paintMusic(true);
    });

    widget.bind(SC.Widget.Events.PAUSE, () => {
        paintMusic(false);
    });

    widget.bind(
        SC.Widget.Events.ERROR,
        musicError
    );

    widget.bind(
        SC.Widget.Events.PLAY_PROGRESS,
        event => {
            if (Date.now() - lastSave > 1000) {
                try {
                    localStorage.setItem(
                        MUSIC,
                        String(event.currentPosition)
                    );
                } catch (_) {}

                lastSave = Date.now();
            }
        }
    );

    widget.bind(SC.Widget.Events.FINISH, () => {
        try {
            localStorage.setItem(MUSIC, "0");
        } catch (_) {}

        widget.seekTo(0);

        if (!explicitPause) {
            widget.play();
        }
    });
};

document.head.appendChild(api);

$("music").addEventListener("click", () => {
    if (!ready) return;

    explicitPause = playing;

    if (playing) {
        widget.pause();
    } else {
        widget.play();
    }
});

// Thử phát khi người dùng tương tác lần đầu.
// Không tự bật lại sau khi người dùng chủ động tắt nhạc.
function firstGesture(event) {
    if (event.target.closest("#music")) return;

    if (
        ready
        && !playing
        && !explicitPause
    ) {
        widget.play();
    }
}

document.addEventListener(
    "click",
    firstGesture,
    { once: true }
);

document.addEventListener(
    "keydown",
    firstGesture,
    { once: true }
);

</script>
</body>
</html>
"""


DATABASE_PATH = Path(__file__).resolve().with_name("love_story_messages.sqlite3")


def sync_letters(event):
    """Chung một SQLite cho mọi phiên; mã tin chống gửi trùng khi kết nối lại."""
    ack = None
    error = None
    with sqlite3.connect(DATABASE_PATH, timeout=15) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS letters (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL UNIQUE,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
        letter = event.get("letter") if isinstance(event, dict) else None
        if letter is not None:
            if (
                isinstance(letter, dict)
                and isinstance(letter.get("id"), str)
                and 1 <= len(letter["id"]) <= 80
                and isinstance(letter.get("sender"), str)
                and 1 <= len(letter["sender"]) <= 80
                and isinstance(letter.get("text"), str)
                and 1 <= len(letter["text"].strip()) <= 3000
            ):
                timestamp = datetime.now(timezone(timedelta(hours=7))).strftime(
                    "%d/%m/%Y %H:%M"
                )
                connection.execute(
                    "INSERT OR IGNORE INTO letters (id, sender, text, time) VALUES (?, ?, ?, ?)",
                    (letter["id"], letter["sender"], letter["text"].strip(), timestamp),
                )
                ack = letter["id"]
            else:
                error = "Chưa lưu được: lời nhắn phải có từ 1 đến 3.000 ký tự."
        rows = connection.execute(
            "SELECT id, sender, text, time FROM letters ORDER BY sequence DESC"
        ).fetchall()
    return [dict(zip(("id", "sender", "text", "time"), row)) for row in rows], ack, error


# ============================================================================
# ĐĂNG KÝ COMPONENT
#
# Component chủ động báo chiều cao nên không phải đặt height cố định.
# Thư mục tạm chỉ chứa giao diện, không chứa nhật ký người dùng.
# ============================================================================

@st.cache_resource
def get_component(html_source):
    folder = Path(
        tempfile.mkdtemp(prefix="love_story_component_")
    )

    (folder / "index.html").write_text(
        html_source,
        encoding="utf-8",
    )

    return components.declare_component(
        "love_story_balanced",
        path=str(folder),
    )


love_story = get_component(HTML)

try:
    shared_messages, ack, sync_error = sync_letters(
        st.session_state.get("love-story-stable")
    )
except sqlite3.Error:
    shared_messages, ack = [], None
    sync_error = "Máy chủ chưa lưu được lời nhắn. Nội dung vẫn còn trong ô nhập, hãy thử lại."

love_story(
    messages=shared_messages,
    ack=ack,
    error=sync_error,
    key="love-story-stable",
    default=None,
)
