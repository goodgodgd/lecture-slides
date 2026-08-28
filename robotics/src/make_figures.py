# -*- coding: utf-8 -*-
"""강의자료에 들어가는 측정 그래프와 개념 그림을 만든다.

숫자는 전부 robotics/examples/ 에서 컨테이너로 실제 측정한 값이다.
측정을 다시 하면 아래 MEASURED 를 고치고 이 스크립트를 다시 돌린다.
    python3 robotics/src/make_figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "Noto Sans CJK JP"   # 한글 글리프가 들어 있는 pan-CJK 폰트
plt.rcParams["font.monospace"] = ["Noto Sans Mono", "DejaVu Sans Mono"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")

FG = "#1a1a1a"
MUTED = "#6b7280"
ACCENT = "#1f5fa8"
BAD = "#c0392b"
GOOD = "#1e7a4f"
WARN = "#a56100"
LINE = "#d4d8de"

# ── 측정값 (컨테이너: 우분투 24.04, g++ -O2) ─────────────────────────
MEASURED = {}


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(path), os.path.getsize(path) // 1024, "KB")


def barh(name, title, labels, values, unit, colors=None, note=None, fmt="{:.1f}"):
    """가로 막대 하나. 값이 크게 차이 날 때 로그 없이도 읽히게 만든다."""
    fig, ax = plt.subplots(figsize=(7.2, 0.72 * len(labels) + 1.5))
    colors = colors or [ACCENT] * len(labels)
    bars = ax.barh(range(len(labels)), values, color=colors, height=0.55)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel(unit, fontsize=10, color=MUTED)
    ax.set_title(title, fontsize=12.5, fontweight="bold", color=FG, pad=12, loc="left")
    top = max(values)
    ax.set_xlim(0, top * 1.22)
    for b, v in zip(bars, values):
        ax.text(b.get_width() + top * 0.02, b.get_y() + b.get_height() / 2,
                fmt.format(v), va="center", fontsize=10.5, color=FG, fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=9.5)
    ax.grid(axis="x", color=LINE, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    if note:
        ax.text(0, -0.20 - 0.02 * len(labels), note, transform=ax.transAxes,
                fontsize=9.5, color=MUTED, va="top")
    save(fig, name)


def box(ax, x, y, w, h, text, fc, ec, fs=10.5, tc=None, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor=ec, linewidth=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc or FG, fontweight="bold" if bold else "normal", linespacing=1.45)


def arrow(ax, xy1, xy2, color=MUTED, style="-|>", lw=1.5, ls="-"):
    ax.add_patch(FancyArrowPatch(xy1, xy2, arrowstyle=style, mutation_scale=14,
                                 color=color, linewidth=lw, linestyle=ls,
                                 shrinkA=2, shrinkB=2))


def canvas(w=7.6, h=3.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


# ══════════════════════════════════════════════════════════════════
# 1회 — 콘 트랙 프로젝트 파이프라인 / 평가 배점
# ══════════════════════════════════════════════════════════════════
def fig_01_pipeline():
    fig, ax = canvas(7.6, 4.4)
    steps = [
        ("/scan\n(거리 r, 각도 θ)", "#e8f0fa", ACCENT, "24회"),
        ("못 쓰는 값 버리기\ninf · NaN · 범위 밖", "#e8f0fa", ACCENT, "24회"),
        ("극좌표를 펴기\nx = r·cosθ,  y = r·sinθ", "#fff5e0", WARN, "25회"),
        ("가까운 점끼리 묶기\n무리 하나 = 콘 하나", "#e7f5ee", GOOD, "27회"),
        ("좌·우 콘 짝짓고\n가운데를 목표점으로", "#e7f5ee", GOOD, "27회"),
        ("/cmd_vel\n(앞으로 얼마, 얼마나 틀어)", "#e8f0fa", ACCENT, "27회"),
    ]
    n = len(steps)
    h = 0.115
    gap = (1.0 - n * h) / (n + 1)
    for i, (txt, fc, ec, when) in enumerate(steps):
        y = 1.0 - gap * (i + 1) - h * (i + 1)
        box(ax, 0.10, y, 0.66, h, txt, fc, ec, fs=10)
        ax.text(0.80, y + h / 2, when, fontsize=9.5, color=MUTED, va="center")
        if i < n - 1:
            arrow(ax, (0.43, y), (0.43, y - gap))
    ax.text(0.10, 1.02, "라이다가 준 숫자가 바퀴 명령이 되기까지", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    ax.text(0.80, 1.02, "배우는 회차", fontsize=9.5, color=MUTED, va="bottom")
    save(fig, "01_project_pipeline.png")


def fig_01_grading():
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    items = ["프로젝트 (주행 26 + 코드·보고서 24)", "과제 7개", "출석·참여"]
    vals = [50, 30, 20]
    colors = [ACCENT, GOOD, MUTED]
    left = 0
    for v, c, lab in zip(vals, colors, items):
        ax.barh([0], [v], left=left, color=c, height=0.42)
        ax.text(left + v / 2, 0, f"{v}%", ha="center", va="center",
                color="white", fontweight="bold", fontsize=12)
        left += v
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.75, 0.75)
    ax.axis("off")
    ax.set_title("100점을 어디서 받나", fontsize=12.5, fontweight="bold",
                 color=FG, loc="left", pad=14)
    for i, (v, c, lab) in enumerate(zip(vals, colors, items)):
        ax.text(0, -0.30 - i * 0.16, "■ " + lab + f"  {v}%", fontsize=10.5, color=c,
                transform=ax.get_yaxis_transform() if False else ax.transData,
                ha="left")
    ax.text(0, 0.55, "프로젝트 50점 중 26점이 실제 주행이다 — 코드가 아니라 로봇이 받는 점수다",
            fontsize=9.8, color=MUTED)
    save(fig, "01_grading.png")


# ══════════════════════════════════════════════════════════════════
# 4회 — 경로 / 표준 출력·오류
# ══════════════════════════════════════════════════════════════════
def fig_04_path_tree():
    fig, ax = canvas(7.6, 3.6)
    rows = [
        (0.02, "/",                    "뿌리. 여기서 모든 길이 시작한다"),
        (0.06, "└─ home/",             ""),
        (0.10, "     └─ ubuntu/",      "여기가 ~ 다"),
        (0.14, "          └─ robot_ws/", ""),
        (0.18, "               └─ src/", "지금 여기에 서 있다고 하자"),
        (0.22, "                    └─ my_pkg/", ""),
    ]
    y0 = 0.93
    for i, (_, path, note) in enumerate(rows):
        y = y0 - i * 0.115
        ax.text(0.03, y, path, fontsize=11.5, family="Noto Sans Mono", color=FG, va="center")
        if note:
            ax.text(0.60, y, note, fontsize=10, color=ACCENT, va="center")
    ax.text(0.03, 0.20, "src/ 에 서 있을 때", fontsize=11, fontweight="bold", color=FG)
    tbl = [("pwd", "/home/ubuntu/robot_ws/src", ""),
           ("cd ..", "/home/ubuntu/robot_ws", "한 칸 위"),
           ("cd ~", "/home/ubuntu", "내 집으로"),
           ("cd ./my_pkg", "/home/ubuntu/robot_ws/src/my_pkg", ". 은 지금 자리")]
    for i, (cmd, res, note) in enumerate(tbl):
        y = 0.13 - i * 0.075
        ax.text(0.05, y, cmd, fontsize=10.5, family="Noto Sans Mono", color=ACCENT, va="center")
        ax.text(0.24, y, "\u2192 " + res, fontsize=10, family="Noto Sans Mono", color=MUTED, va="center")
        if note:
            ax.text(0.76, y, "\u2190 " + note, fontsize=9.6, color=ACCENT, va="center")
    ax.set_ylim(-0.20, 1.0)
    ax.text(0.03, 1.02, "~ · . · .. 가 각각 어디를 가리키나", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    save(fig, "04_path_tree.png")


def fig_04_streams():
    fig, ax = canvas(7.6, 3.2)
    box(ax, 0.05, 0.42, 0.26, 0.26, "명령어\nls hello.sh no_such", "#f8f9fb", MUTED, fs=10)
    box(ax, 0.52, 0.66, 0.30, 0.20, "1번 관 — 표준 출력\nhello.sh", "#e7f5ee", GOOD, fs=10)
    box(ax, 0.52, 0.24, 0.30, 0.20, "2번 관 — 표준 오류\nNo such file...", "#fdecea", BAD, fs=10)
    arrow(ax, (0.31, 0.60), (0.52, 0.76), color=GOOD)
    arrow(ax, (0.31, 0.50), (0.52, 0.34), color=BAD)
    ax.text(0.86, 0.76, "화면", fontsize=10.5, color=MUTED, va="center")
    ax.text(0.86, 0.34, "화면", fontsize=10.5, color=MUTED, va="center")
    ax.text(0.05, 0.10, "> out.txt", fontsize=10.5, color=FG, family="Noto Sans Mono")
    ax.text(0.24, 0.10, "1번만 파일로 보낸다 \u2192 오류는 화면에 그대로 남는다",
            fontsize=10.2, color=FG)
    ax.text(0.05, 0.02, "> all.txt 2>&1", fontsize=10.5, color=FG, family="Noto Sans Mono")
    ax.text(0.24, 0.02, "2번을 1번 쪽으로 합친다 \u2192 둘 다 파일로 간다",
            fontsize=10.2, color=FG)
    ax.set_ylim(-0.05, 1.0)
    ax.text(0.05, 0.95, "명령어는 관을 두 개 갖고 있다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    save(fig, "04_streams.png")


# ══════════════════════════════════════════════════════════════════
# 6회 — C++ vs 파이썬 / AI 코드의 특성
# ══════════════════════════════════════════════════════════════════
def fig_06_cpp_vs_python():
    barh("06_cpp_vs_python.png",
         "같은 계산을 시켰을 때 걸린 시간",
         ["C++  (g++ 13.3, -O2)", "파이썬 3.12"],
         [23.6, 3963.8], "밀리초 (작을수록 빠르다)",
         colors=[GOOD, BAD],
         note="라이다 한 스캔(360개)에서 못 쓰는 값을 걸러 평균을 내는 일을 10만 번.\n"
              "같은 결과(평균 2.8000 m)를 냈고 파이썬이 168배 오래 걸렸다.\n"
              "잰 곳: 컨테이너(우분투 24.04.4, g++ 13.3.0 -O2 / CPython 3.12.3)")


def fig_06_ai_vs_human():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    labels = ["복사·할당 오버헤드", "명시적 for 루프", "표준 라이브러리 사용", "정확성·안전성 문제"]
    vals = [1.39, 2.0, 0.4, 0.94]
    colors = [BAD, BAD, WARN, GOOD]
    ys = range(len(labels))
    ax.barh(ys, vals, color=colors, height=0.5)
    ax.axvline(1.0, color=FG, linewidth=1.4, linestyle="--")
    ax.text(1.02, len(labels) - 0.35, "1.0 = 사람이 쓴 코드와 같음", fontsize=9.5, color=FG)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 2.35)
    ax.set_xlabel("AI ÷ 사람 (배)", fontsize=10, color=MUTED)
    ax.set_title("AI가 짠 C++ 코드는 사람이 짠 것과 어디가 달랐나",
                 fontsize=12.5, fontweight="bold", color=FG, pad=12, loc="left")
    for y, v in zip(ys, vals):
        ax.text(v + 0.04, y, f"{v}배", va="center", fontsize=10.5, fontweight="bold", color=FG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(LINE); ax.spines["bottom"].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=9.5)
    ax.grid(axis="x", color=LINE, linewidth=0.6, alpha=0.7); ax.set_axisbelow(True)
    ax.text(0, -0.30, "맨 아래 줄이 중요하다 — AI는 틀린 코드를 더 많이 만들지 않았다.\n"
                      "문제는 맞지만 둔한 코드다. 위 세 줄이 그것이다.",
            transform=ax.transAxes, fontsize=9.8, color=MUTED, va="top")
    save(fig, "06_ai_vs_human.png")


# ══════════════════════════════════════════════════════════════════
# 7회 — 헤더와 소스
# ══════════════════════════════════════════════════════════════════
def fig_07_header_source():
    fig, ax = canvas(7.6, 3.4)
    box(ax, 0.04, 0.55, 0.40, 0.34,
        "scan_filter.hpp  (헤더)\n\n\"무엇이 있는지\"만 적는다\nstd::vector<float> keep_valid(...);",
        "#e8f0fa", ACCENT, fs=10)
    box(ax, 0.56, 0.55, 0.40, 0.34,
        "scan_filter.cpp  (소스)\n\n\"어떻게 하는지\"를 적는다\n{ ... 실제 코드 ... }",
        "#e7f5ee", GOOD, fs=10)
    box(ax, 0.30, 0.10, 0.40, 0.26, "main.cpp\n#include \"scan_filter.hpp\"\n헤더만 읽으면 쓸 수 있다",
        "#f8f9fb", MUTED, fs=10)
    arrow(ax, (0.24, 0.55), (0.42, 0.36), color=ACCENT)
    arrow(ax, (0.76, 0.55), (0.58, 0.36), color=GOOD, style="-", ls=":")
    ax.text(0.60, 0.44, "빌드할 때 붙는다", fontsize=9.3, color=GOOD)
    ax.text(0.10, 0.44, "#include 로 읽는다", fontsize=9.3, color=ACCENT)
    ax.text(0.04, 0.96, "선언과 정의를 두 파일로 나눈다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    ax.set_ylim(0.02, 1.02)
    save(fig, "07_header_source.png")


# ══════════════════════════════════════════════════════════════════
# 8회 — 멤버 초기화 리스트
# ══════════════════════════════════════════════════════════════════
def fig_08_init_list():
    fig, ax = canvas(7.6, 3.2)
    ax.text(0.04, 0.94, "생성자 안에서 대입하면 두 번 일한다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    box(ax, 0.04, 0.56, 0.26, 0.24, "① 빈 문자열로\n먼저 만든다", "#fdecea", BAD, fs=10)
    box(ax, 0.36, 0.56, 0.26, 0.24, "② 그 위에\n값을 덮어쓴다", "#fdecea", BAD, fs=10)
    arrow(ax, (0.30, 0.68), (0.36, 0.68), color=BAD)
    ax.text(0.66, 0.68, "name_ = n;", fontsize=11, family="Noto Sans Mono", color=BAD, va="center")
    box(ax, 0.04, 0.18, 0.26, 0.24, "① 값을 넣은 채로\n한 번에 만든다", "#e7f5ee", GOOD, fs=10)
    ax.text(0.36, 0.30, ": name_(n)", fontsize=11, family="Noto Sans Mono", color=GOOD, va="center")
    ax.text(0.04, 0.06, "3백만 번 만들어 재 보니 대입 방식이 47.2 ms, 초기화 리스트가 40.5 ms — 1.17배 차이.",
            fontsize=9.8, color=MUTED)
    ax.text(0.04, 0.005, "잰 곳: 컨테이너(우분투 24.04.4, g++ 13.3.0 -O2)  ·  멤버가 std::string 하나일 때다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(-0.02, 1.02)
    save(fig, "08_init_list.png")


# ══════════════════════════════════════════════════════════════════
# 9회 — 빌드 3단계와 오류가 나는 자리
# ══════════════════════════════════════════════════════════════════
def fig_09_build_stages():
    fig, ax = canvas(7.6, 3.6)
    stages = [
        ("① cmake\n설정", "#e8f0fa", ACCENT, "CMake Error at\nCMakeLists.txt:7", "CMakeLists.txt"),
        ("② 컴파일\n소스 → .o", "#fff5e0", WARN, "error: expected ';'\nbefore 'return'", "소스 파일(.cpp)"),
        ("③ 링크\n.o → 실행 파일", "#fdecea", BAD, "undefined reference\nto `mean_range(...)'", "CMakeLists.txt\n(target_link_libraries)"),
    ]
    w = 0.28
    for i, (t, fc, ec, err, fix) in enumerate(stages):
        x = 0.03 + i * 0.325
        box(ax, x, 0.68, w, 0.22, t, fc, ec, fs=10.5, bold=True)
        box(ax, x, 0.36, w, 0.22, err, "#f8f9fb", MUTED, fs=8.8)
        ax.text(x + w / 2, 0.26, "고칠 곳", fontsize=9, color=MUTED, ha="center")
        ax.text(x + w / 2, 0.16, fix, fontsize=9.4, color=ec, ha="center",
                fontweight="bold", va="top")
        if i < 2:
            arrow(ax, (x + w, 0.79), (x + 0.325, 0.79))
        ax.add_patch(FancyArrowPatch((x + w / 2, 0.68), (x + w / 2, 0.58),
                                     arrowstyle="-|>", mutation_scale=12, color=MUTED, linewidth=1.2))
    ax.text(0.03, 0.96, "빌드는 세 단계다 — 어느 단계에서 났는지가 고칠 곳을 정한다",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")
    ax.text(0.03, 0.03, "세 번째가 학생을 가장 많이 괴롭힌다. 코드는 멀쩡한데 링크에서 터지므로 소스만 들여다보게 된다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(0.0, 1.02)
    save(fig, "09_build_stages.png")


# ══════════════════════════════════════════════════════════════════
# 10회 — 가상 소멸자 / RAII
# ══════════════════════════════════════════════════════════════════
def fig_10_virtual_dtor():
    fig, ax = canvas(7.6, 3.6)
    ax.text(0.03, 0.95, "기반 클래스 포인터로 지울 때 무슨 일이 생기나",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")
    # 왼쪽 — virtual 없음
    ax.text(0.03, 0.83, "virtual 이 없을 때", fontsize=11, color=BAD, fontweight="bold")
    box(ax, 0.03, 0.52, 0.42, 0.24, "unique_ptr<Sensor> 가 사라진다\n↓\nSensor 소멸자만 불린다",
        "#fdecea", BAD, fs=10)
    box(ax, 0.03, 0.24, 0.42, 0.22, "Lidar 소멸자는 안 불린다\nfloat 360칸이 그대로 남는다",
        "#fdecea", BAD, fs=10)
    arrow(ax, (0.24, 0.52), (0.24, 0.46), color=BAD)
    # 오른쪽 — virtual 있음
    ax.text(0.55, 0.83, "virtual 을 붙였을 때", fontsize=11, color=GOOD, fontweight="bold")
    box(ax, 0.55, 0.52, 0.42, 0.24, "unique_ptr<Sensor> 가 사라진다\n↓\nLidar 소멸자가 먼저 불린다",
        "#e7f5ee", GOOD, fs=10)
    box(ax, 0.55, 0.24, 0.42, 0.22, "이어서 Sensor 소멸자\n360칸이 반납된다",
        "#e7f5ee", GOOD, fs=10)
    arrow(ax, (0.76, 0.52), (0.76, 0.46), color=GOOD)
    ax.text(0.03, 0.10, "실행해서 확인한 것이다 — 왼쪽에서는 「LidarBad 소멸자」 줄이 화면에 아예 찍히지 않는다.",
            fontsize=9.8, color=MUTED)
    ax.text(0.03, 0.03, "크래시도 안 나고 오류 메시지도 없다. 그래서 이 버그는 오래 살아남는다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(0.0, 1.02)
    save(fig, "10_virtual_dtor.png")


def fig_10_raii():
    fig, ax = canvas(7.6, 3.3)
    ax.text(0.03, 0.95, "중괄호 하나가 곧 수명이다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    rows = [("{", 0.80, "여는 중괄호", ACCENT),
            ("  std::ofstream f(\"out.txt\");", 0.66, "여기서 파일이 열린다", GOOD),
            ("  f << \"scan 0.83\";", 0.52, "쓴다", FG),
            ("}", 0.38, "닫는 중괄호 — 여기서 자동으로 닫힌다", GOOD)]
    for txt, y, note, c in rows:
        ax.text(0.05, y, txt, fontsize=11.5, family="Noto Sans Mono", color=FG, va="center")
        ax.text(0.52, y, "← " + note, fontsize=10, color=c, va="center")
    ax.add_patch(FancyBboxPatch((0.035, 0.33), 0.45, 0.53,
                                boxstyle="round,pad=0.008,rounding_size=0.02",
                                facecolor="none", edgecolor=ACCENT, linewidth=1.3, linestyle="--"))
    ax.text(0.05, 0.22, "close() 를 부른 곳이 한 군데도 없다.", fontsize=10.5, color=FG)
    ax.text(0.05, 0.13, "잠금(std::lock_guard)도, 메모리(unique_ptr)도 전부 같은 방식으로 정리된다.",
            fontsize=10, color=MUTED)
    ax.text(0.05, 0.04, "이것이 RAII다 — 짝 맞추는 일을 사람이 하지 않는다.", fontsize=10, color=MUTED)
    ax.set_ylim(0.0, 1.02)
    save(fig, "10_raii_scope.png")


# ══════════════════════════════════════════════════════════════════
# 11회 — 복사 비용
# ══════════════════════════════════════════════════════════════════
def fig_11_copy_cost():
    barh("11_copy_cost.png",
         "라이다 메시지를 콜백에 10만 번 넘기는 데 걸린 시간",
         ["값으로 받기  (ScanMsg msg)", "const 참조로 받기  (const ScanMsg & msg)"],
         [3.66, 0.17], "밀리초 (작을수록 빠르다)",
         colors=[BAD, GOOD], fmt="{:.2f}",
         note="한 메시지에 float 360개. 하는 일은 ranges[0] 을 읽는 것뿐이고 두 코드가 똑같다.\n"
              "달라진 것은 함수 인자 앞의 const & 두 글자뿐인데 22배가 났다.\n"
              "잰 곳: 컨테이너(우분투 24.04.4, g++ 13.3.0 -O2)")


def fig_11_value_vs_ref():
    fig, ax = canvas(7.6, 3.2)
    ax.text(0.03, 0.95, "값으로 받는다는 것은 사본을 하나 더 만든다는 뜻이다",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")
    box(ax, 0.03, 0.58, 0.24, 0.22, "원본 메시지\nfloat 360개", "#f8f9fb", MUTED, fs=10)
    box(ax, 0.40, 0.58, 0.24, 0.22, "사본 ①\nfloat 360개", "#fdecea", BAD, fs=10)
    box(ax, 0.72, 0.58, 0.24, 0.22, "사본 ②\nfloat 360개", "#fdecea", BAD, fs=10)
    arrow(ax, (0.27, 0.69), (0.40, 0.69), color=BAD)
    arrow(ax, (0.64, 0.69), (0.72, 0.69), color=BAD)
    ax.text(0.28, 0.83, "값으로 받음", fontsize=9.4, color=BAD)
    ax.text(0.63, 0.83, "안에서 또 복사", fontsize=9.4, color=BAD)
    box(ax, 0.03, 0.18, 0.24, 0.22, "원본 메시지\nfloat 360개", "#f8f9fb", MUTED, fs=10)
    box(ax, 0.40, 0.18, 0.30, 0.22, "이름표만 하나 더\n(복사 0개)", "#e7f5ee", GOOD, fs=10)
    arrow(ax, (0.40, 0.29), (0.27, 0.29), color=GOOD)
    ax.text(0.28, 0.43, "const & 로 받음", fontsize=9.4, color=GOOD)
    ax.text(0.03, 0.06, "라이다는 초당 5번 들어온다. 위쪽은 초당 3,600개를 아무 이득 없이 새로 만든다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(0.0, 1.02)
    save(fig, "11_value_vs_ref.png")


def fig_11_move():
    fig, ax = canvas(7.6, 3.4)
    ax.text(0.03, 0.95, "복사는 알맹이를 새로 만들고, 이동은 알맹이를 넘긴다",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")

    ax.text(0.03, 0.80, "복사 — 원본은 그대로 남는다", fontsize=10.5, color=BAD, fontweight="bold")
    box(ax, 0.03, 0.52, 0.26, 0.22, "tmp\nfloat 360개", "#f8f9fb", MUTED, fs=10)
    box(ax, 0.53, 0.52, 0.30, 0.22, "taken\nfloat 360개 (새로 만듦)", "#fdecea", BAD, fs=10)
    arrow(ax, (0.29, 0.63), (0.53, 0.63), color=BAD)
    ax.text(0.31, 0.75, "360개를 새로 만들어 채운다", fontsize=9.4, color=BAD)

    ax.text(0.03, 0.38, "이동 — std::move 로 넘기면 원본이 빈다", fontsize=10.5, color=GOOD, fontweight="bold")
    box(ax, 0.03, 0.10, 0.26, 0.22, "tmp\nsize() = 0", "#fff5e0", WARN, fs=10)
    box(ax, 0.53, 0.10, 0.30, 0.22, "taken\nfloat 360개 (그 알맹이)", "#e7f5ee", GOOD, fs=10)
    arrow(ax, (0.29, 0.21), (0.53, 0.21), color=GOOD)
    ax.text(0.31, 0.33, "알맹이의 주인만 바뀐다", fontsize=9.4, color=GOOD)
    ax.text(0.85, 0.21, "넘겨준 뒤\n읽으면 안 된다", fontsize=9.3, color=WARN, va="center")

    ax.text(0.03, -0.02, "세어 보니 복사 0회 · 이동 1회. 넘겨준 쪽 tmp.ranges.size() 가 0이 됐다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(-0.08, 1.02)
    save(fig, "11_move.png")


# ══════════════════════════════════════════════════════════════════
# 12회 — reserve / 소유권
# ══════════════════════════════════════════════════════════════════
def fig_12_reserve():
    barh("12_reserve_bench.png",
         "360개짜리 vector 를 10만 번 채우는 데 걸린 시간",
         ["reserve() 없이", "reserve(360) 하고"],
         [34.2, 18.1], "밀리초 (작을수록 빠르다)",
         colors=[WARN, GOOD],
         note="reserve 없이 채우면 자리가 모자랄 때마다 더 큰 자리를 새로 잡고 있던 값을 옮긴다.\n"
              "실제로 세어 보니 360개를 담는 동안 자리를 10번 다시 잡았다(최종 capacity 512).\n"
              "잰 곳: 컨테이너(우분투 24.04.4, g++ 13.3.0 -O2)")


def fig_12_ownership():
    fig, ax = canvas(7.6, 3.2)
    ax.text(0.03, 0.95, "주인이 하나인가, 여럿인가", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    ax.text(0.03, 0.82, "unique_ptr — 주인이 하나", fontsize=11, color=GOOD, fontweight="bold")
    box(ax, 0.03, 0.54, 0.16, 0.20, "a", "#e7f5ee", GOOD, fs=11)
    box(ax, 0.40, 0.54, 0.24, 0.20, "라이다 객체", "#f8f9fb", MUTED, fs=10)
    arrow(ax, (0.19, 0.64), (0.40, 0.64), color=GOOD)
    ax.text(0.68, 0.64, "move 하면 주인이\nb 로 바뀐다 (복사 안 됨)", fontsize=9.5, color=MUTED, va="center")
    ax.text(0.03, 0.44, "shared_ptr — 여럿이 나눠 가짐", fontsize=11, color=ACCENT, fontweight="bold")
    box(ax, 0.03, 0.20, 0.13, 0.18, "p1", "#e8f0fa", ACCENT, fs=11)
    box(ax, 0.03, 0.00, 0.13, 0.18, "p2", "#e8f0fa", ACCENT, fs=11)
    box(ax, 0.40, 0.10, 0.24, 0.20, "카메라 객체\n주인 수 2", "#f8f9fb", MUTED, fs=10)
    arrow(ax, (0.16, 0.29), (0.40, 0.24), color=ACCENT)
    arrow(ax, (0.16, 0.09), (0.40, 0.16), color=ACCENT)
    ax.text(0.68, 0.20, "마지막 한 명이 사라질 때\n객체가 꺼진다", fontsize=9.5, color=MUTED, va="center")
    ax.set_ylim(-0.04, 1.02)
    save(fig, "12_ownership.png")


# ══════════════════════════════════════════════════════════════════
# 13회 — 정렬 속도 / NaN
# ══════════════════════════════════════════════════════════════════
def fig_13_sort_speed():
    barh("13_sort_speed.png",
         "360개를 정렬해 중앙값을 얻는 일을 1만 번",
         ["직접 짠 선택 정렬", "std::sort", "std::nth_element"],
         [364.5, 21.2, 5.2], "밀리초 (작을수록 빠르다)",
         colors=[BAD, GOOD, ACCENT],
         note="같은 입력, 같은 결과다. std::sort 가 17.2배, nth_element 가 69.8배 빨랐다.\n"
              "중앙값 하나만 필요하면 전부 정렬할 필요도 없다는 것을 nth_element 가 보여 준다.\n"
              "잰 곳: 컨테이너(우분투 24.04.4, g++ 13.3.0 -O2)")


def fig_13_nan():
    fig, ax = canvas(7.6, 3.4)
    ax.text(0.03, 0.95, "NaN 이 섞이면 최솟값 찾기의 답이 자리마다 달라진다",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")
    ax.text(0.03, 0.83, "NaN 은 어떤 비교에도 거짓을 낸다", fontsize=11, color=BAD, fontweight="bold")
    for i, (q, a) in enumerate([("NaN < 5.0", "거짓"), ("NaN > 5.0", "거짓"), ("NaN == NaN", "거짓")]):
        ax.text(0.05 + i * 0.24, 0.72, q, fontsize=10.5, family="Noto Sans Mono", color=FG)
        ax.text(0.05 + i * 0.24, 0.63, "→ " + a, fontsize=10.5, color=BAD)
    rows = [("[NaN, 3.0, 0.5, 2.0]", "nan", BAD),
            ("[3.0, NaN, 0.5, 2.0]", "0.50", WARN),
            ("[3.0, 0.5, 2.0]", "0.50", GOOD)]
    ax.text(0.03, 0.48, "같은 값 묶음인데 NaN 의 자리만 바꿔 min_element 를 돌린 결과",
            fontsize=10.5, color=FG, fontweight="bold")
    for i, (arr, res, c) in enumerate(rows):
        y = 0.36 - i * 0.10
        ax.text(0.05, y, arr, fontsize=10.5, family="Noto Sans Mono", color=FG)
        ax.text(0.52, y, "→  " + res, fontsize=10.5, family="Noto Sans Mono", color=c, fontweight="bold")
    ax.text(0.03, 0.02, "문법도 논리도 맞는 코드가 입력에 따라 다른 답을 낸다. 실제로 돌려서 얻은 결과다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(-0.02, 1.02)
    save(fig, "13_nan_compare.png")


# ══════════════════════════════════════════════════════════════════
# 14회 — 캡처
# ══════════════════════════════════════════════════════════════════
def fig_14_capture():
    fig, ax = canvas(7.6, 3.4)
    ax.text(0.03, 0.95, "대괄호 안에 무엇을 적느냐가 캡처다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    rows = [
        ("[this]",  "이 객체의 멤버를 쓴다", "멤버 하나를 쓸 때. 노드 콜백의 기본값", GOOD),
        ("[&x]",    "x 만 원본을 가리킨다", "무엇을 쓰는지 코드에 드러난다", GOOD),
        ("[&]",     "바깥의 모든 것을 원본으로", "편하지만 무엇을 쓰는지 안 보인다", WARN),
        ("[=]",     "바깥의 모든 것을 복사로", "큰 것이 통째로 복사된다", BAD),
    ]
    for i, (cap, mean, when, c) in enumerate(rows):
        y = 0.72 - i * 0.155
        ax.text(0.05, y, cap, fontsize=12, family="Noto Sans Mono", color=c, fontweight="bold")
        ax.text(0.20, y, mean, fontsize=10.5, color=FG)
        ax.text(0.55, y, when, fontsize=10, color=MUTED)
    ax.text(0.03, 0.10, "float 360개를 담은 객체를 [=] 로 캡처하니 복사가 1회, [&big] 로 캡처하니 0회였다.",
            fontsize=9.8, color=MUTED)
    ax.text(0.03, 0.02, "복사 생성자에 세는 코드를 넣어 실제로 센 것이다(컨테이너, g++ 13.3.0 -O2).",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(-0.02, 1.02)
    save(fig, "14_capture_kinds.png")


def fig_14_optional():
    fig, ax = canvas(7.6, 3.0)
    ax.text(0.03, 0.95, "\"값이 없음\"을 -1 로 말하면 받는 쪽이 검사를 빠뜨린다",
            fontsize=12.5, fontweight="bold", color=FG, va="bottom")
    box(ax, 0.03, 0.50, 0.43, 0.30,
        "float nearest(...)\n\n실패하면 -1.0f 를 돌려준다\n→ 받는 쪽이 -1 인지 볼 의무가 생긴다",
        "#fdecea", BAD, fs=10)
    box(ax, 0.54, 0.50, 0.43, 0.30,
        "std::optional<float> nearest(...)\n\n실패하면 nullopt 를 돌려준다\n→ 값을 꺼내려면 검사를 지나야 한다",
        "#e7f5ee", GOOD, fs=10)
    ax.text(0.03, 0.34, "-1.0 이 거리인지 실패인지 코드만 봐서는 알 수 없다.", fontsize=10, color=BAD)
    ax.text(0.54, 0.34, "if (!v) 한 줄로 걸러진다.", fontsize=10, color=GOOD)
    ax.text(0.03, 0.14, "라이다 값이 전부 inf·NaN 인 순간은 실제로 생긴다 — 로봇이 아무것도 못 보는 방향을 향했을 때다.",
            fontsize=9.8, color=MUTED)
    ax.text(0.03, 0.05, "그때 -1 을 거리로 읽으면 로봇은 「뒤쪽 1 m 에 벽이 있다」고 판단한다.",
            fontsize=9.8, color=MUTED)
    ax.set_ylim(0.0, 1.02)
    save(fig, "14_optional.png")


# ══════════════════════════════════════════════════════════════════
# 3회 — 챗봇과 에이전트
# ══════════════════════════════════════════════════════════════════
def fig_03_chatbot_agent():
    fig, ax = canvas(7.6, 3.2)
    ax.text(0.03, 0.95, "챗봇은 답을 주고, 에이전트는 일을 한다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")
    ax.text(0.03, 0.83, "챗봇", fontsize=11, color=MUTED, fontweight="bold")
    for i, t in enumerate(["내가 묻는다", "글로 답이 온다", "내가 복사해서 붙인다", "내가 실행한다"]):
        x = 0.03 + i * 0.245
        box(ax, x, 0.56, 0.215, 0.18, t, "#f8f9fb", MUTED, fs=9.3)
        if i < 3:
            arrow(ax, (x + 0.215, 0.65), (x + 0.245, 0.65))
    ax.text(0.03, 0.44, "에이전트", fontsize=11, color=ACCENT, fontweight="bold")
    for i, t in enumerate(["내가 시킨다", "파일을 직접 고친다", "명령을 직접 실행한다", "내가 결과를 확인한다"]):
        x = 0.03 + i * 0.245
        fc, ec = ("#e8f0fa", ACCENT) if i < 3 else ("#fff5e0", WARN)
        box(ax, x, 0.17, 0.215, 0.18, t, fc, ec, fs=9.3)
        if i < 3:
            arrow(ax, (x + 0.215, 0.26), (x + 0.245, 0.26), color=ACCENT)
    ax.text(0.03, 0.05, "마지막 칸만 색이 다르다. 확인은 넘길 수 없기 때문이다 — "
                        "「잘 됐는지 봐 줘」라고 하면 「완료했습니다」라는 답이 온다.",
            fontsize=9.8, color=WARN)
    ax.set_ylim(0.0, 1.02)
    save(fig, "03_chatbot_vs_agent.png")


def fig_04_env_scope():
    """4회 — 환경변수가 어디까지 따라가나. bash 실행과 source 의 차이."""
    fig, ax = canvas(7.6, 4.0)
    ax.text(0.01, 1.02, "환경변수는 아래로만 흐른다", fontsize=12.5,
            fontweight="bold", color=FG, va="bottom")

    box(ax, 0.01, 0.78, 0.42, 0.17, "터미널 A\nexport MY_ROBOT=burger",
        "#e8f0fa", ACCENT, fs=10.2)
    box(ax, 0.01, 0.52, 0.42, 0.17, "A 에서 띄운 자식 셸\n$MY_ROBOT \u2192 burger",
        "#e7f5ee", GOOD, fs=10.2)
    arrow(ax, (0.22, 0.78), (0.22, 0.69), color=GOOD)
    ax.text(0.245, 0.735, "물려받는다", fontsize=9.6, color=GOOD, va="center")

    box(ax, 0.55, 0.78, 0.42, 0.17, "따로 연 터미널 B\n$MY_ROBOT \u2192 (빈칸)",
        "#fdecea", BAD, fs=10.2)
    arrow(ax, (0.43, 0.865), (0.55, 0.865), color=BAD, style="-|>", ls="--")
    ax.text(0.49, 0.905, "X", fontsize=12, color=BAD, ha="center", va="center",
            fontweight="bold")
    ax.text(0.55, 0.71, "옆으로도, 위로도 가지 않는다", fontsize=9.6, color=BAD, va="center")

    ax.text(0.01, 0.40, "같은 파일 setenv.sh 를 두 가지로 실행했을 때",
            fontsize=11, fontweight="bold", color=FG, va="center")
    rows = [
        ("bash setenv.sh", "새 셸이 열려 거기서 export 하고 그 셸이 끝난다", "[ ]", BAD),
        ("source setenv.sh", "지금 이 셸이 그 파일을 직접 읽는다", "[LDS-02]", GOOD),
    ]
    for i, (cmd, why, res, col) in enumerate(rows):
        y = 0.28 - i * 0.13
        ax.text(0.02, y, cmd, fontsize=10.5, family="Noto Sans Mono", color=ACCENT, va="center")
        ax.text(0.31, y, "\u2192 " + why, fontsize=10, color=FG, va="center")
        ax.text(0.86, y, res, fontsize=10.5, family="Noto Sans Mono",
                color=col, fontweight="bold", va="center")
    ax.text(0.02, 0.015,
            "그래서 새 터미널을 열 때마다 source 를 다시 하거나, .bashrc 에 적어 둔다",
            fontsize=10, color=MUTED, va="center")
    ax.set_ylim(-0.03, 1.0)
    save(fig, "04_env_scope.png")


if __name__ == "__main__":
    for fn in [fig_01_pipeline, fig_01_grading, fig_03_chatbot_agent,
               fig_04_path_tree, fig_04_streams, fig_04_env_scope,
               fig_06_cpp_vs_python, fig_06_ai_vs_human, fig_07_header_source,
               fig_08_init_list, fig_09_build_stages,
               fig_10_virtual_dtor, fig_10_raii,
               fig_11_copy_cost, fig_11_value_vs_ref, fig_11_move,
               fig_12_reserve, fig_12_ownership,
               fig_13_sort_speed, fig_13_nan, fig_14_capture, fig_14_optional]:
        fn()
