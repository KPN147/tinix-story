"""
Module lưu từng chương thành file .md riêng lẻ và tổng hợp thành file .md duy nhất.

Cấu trúc thư mục:
    output/
    └── {project_title}/
        ├── Chuong_01_TieuDe.md
        ├── Chuong_02_TieuDe.md
        ├── ...
        └── {project_title}_full.md  (file tổng hợp)
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def _sanitize_filename(name: str) -> str:
    """Loại bỏ ký tự đặc biệt khỏi tên file, giữ tiếng Việt."""
    # Thay thế các ký tự không hợp lệ cho filename
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Thay khoảng trắng thừa thành _
    name = re.sub(r'\s+', '_', name.strip())
    # Giới hạn độ dài
    if len(name) > 80:
        name = name[:80]
    return name


def _get_project_dir(project_title: str) -> str:
    """Tạo và trả về đường dẫn thư mục output cho project."""
    safe_title = _sanitize_filename(project_title)
    project_dir = os.path.join(OUTPUT_DIR, safe_title)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def save_chapter_md(
    project_title: str,
    chapter_num: int,
    chapter_title: str,
    content: str,
    genre: str = "",
    word_count: int = 0
) -> Tuple[bool, str]:
    """
    Lưu một chương thành file .md riêng lẻ.

    Args:
        project_title: Tên dự án
        chapter_num: Số thứ tự chương
        chapter_title: Tiêu đề chương
        content: Nội dung chương
        genre: Thể loại (tùy chọn, để ghi metadata)
        word_count: Số từ (tùy chọn)

    Returns:
        (success, file_path hoặc error_message)
    """
    if not content or not content.strip():
        return False, "Nội dung chương trống"

    try:
        project_dir = _get_project_dir(project_title)
        safe_chapter_title = _sanitize_filename(chapter_title)
        filename = f"Chuong_{chapter_num:02d}_{safe_chapter_title}.md"
        filepath = os.path.join(project_dir, filename)

        # Xây dựng nội dung Markdown
        wc = word_count if word_count else len(content)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_content = f"# Chương {chapter_num}: {chapter_title}\n\n"
        md_content += f"> 📖 **{project_title}**"
        if genre:
            md_content += f" | 🏷️ {genre}"
        md_content += f" | 📝 {wc} từ | 🕐 {now}\n\n"
        md_content += "---\n\n"
        md_content += content.strip()
        md_content += "\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"Chapter saved as MD: {filepath}")
        return True, filepath

    except Exception as e:
        logger.error(f"Failed to save chapter MD: {e}")
        return False, str(e)


def combine_chapters_md(
    project_title: str,
    chapters: list,
    genre: str = "",
    character_setting: str = "",
    world_setting: str = ""
) -> Tuple[bool, str]:
    """
    Tổng hợp tất cả các chương thành 1 file .md duy nhất.

    Args:
        project_title: Tên dự án
        chapters: Danh sách đối tượng Chapter (có .num, .title, .content, .word_count)
        genre: Thể loại
        character_setting: Thiết lập nhân vật
        world_setting: Thiết lập thế giới quan

    Returns:
        (success, file_path hoặc error_message)
    """
    completed = [ch for ch in chapters if getattr(ch, 'content', None)]
    if not completed:
        return False, "Không có chương nào đã hoàn thành để tổng hợp."

    try:
        project_dir = _get_project_dir(project_title)
        safe_title = _sanitize_filename(project_title)
        filename = f"{safe_title}_full.md"
        filepath = os.path.join(project_dir, filename)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_words = sum(ch.word_count for ch in completed if ch.word_count)
        total_chapters = len(chapters)
        completed_count = len(completed)

        # Header
        md = f"# {project_title}\n\n"
        md += f"> 📊 **{completed_count}/{total_chapters}** chương | "
        md += f"📝 **{total_words:,}** từ | "
        if genre:
            md += f"🏷️ **{genre}** | "
        md += f"🕐 Tổng hợp lúc: {now}\n\n"

        # Metadata
        if character_setting or world_setting:
            md += "---\n\n"
            if character_setting:
                md += "<details>\n<summary>🎭 Thiết lập nhân vật</summary>\n\n"
                md += character_setting.strip() + "\n\n</details>\n\n"
            if world_setting:
                md += "<details>\n<summary>🌍 Thiết lập thế giới quan</summary>\n\n"
                md += world_setting.strip() + "\n\n</details>\n\n"

        # Mục lục
        md += "---\n\n## 📑 Mục lục\n\n"
        for ch in completed:
            wc = ch.word_count if ch.word_count else len(ch.content)
            md += f"- **Chương {ch.num}**: {ch.title} ({wc:,} từ)\n"
        md += "\n---\n\n"

        # Nội dung từng chương
        for ch in sorted(completed, key=lambda x: x.num):
            md += f"## Chương {ch.num}: {ch.title}\n\n"
            md += ch.content.strip()
            md += "\n\n---\n\n"

        # Footer
        md += f"*— Tổng hợp bởi TiniX Story | {now} —*\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        logger.info(f"Combined MD saved: {filepath} ({completed_count} chapters, {total_words} words)")
        return True, filepath

    except Exception as e:
        logger.error(f"Failed to combine chapters MD: {e}")
        return False, str(e)
