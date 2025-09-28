import gzip
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom


def write_to_xml(programmes, path):
    """
    将 programmes 写入 EPG XML：
    - 为每个频道创建 channel/display-name
    - 对节目信息进行排序（按 start 时间）与去重（start/stop/title）
    - 过滤无效节目（缺少 title/start/stop）
    """
    root = ET.Element('tv', attrib={'date': datetime.now().strftime("%Y%m%d%H%M%S +0800")})
    for channel_id, data in programmes.items():
        # 频道定义
        channel_elem = ET.SubElement(root, 'channel', attrib={"id": channel_id})
        display_name_elem = ET.SubElement(channel_elem, 'display-name', attrib={"lang": "zh"})
        display_name_elem.text = channel_id

        # 排序与去重
        # 按 start 字符串排序（移除空格），避免乱序
        sorted_programmes = sorted(
            data,
            key=lambda p: (p.get('start', '') or '').replace(' ', '')
        )
        seen = set()
        for prog in sorted_programmes:
            title_elem = prog.find('title')
            title_text = (title_elem.text.strip() if title_elem is not None and title_elem.text else '')
            start = prog.get('start', '').strip()
            stop = prog.get('stop', '').strip()

            # 过滤无效项
            if not title_text or not start or not stop:
                continue

            # 去重：以 (start, stop, title_text) 作为唯一键
            key = (start, stop, title_text)
            if key in seen:
                continue
            seen.add(key)

            # 绑定频道并追加
            prog.set('channel', channel_id)
            root.append(prog)

    # 写入文件（pretty print）
    with open(path, 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent='\t', newl='\n'))


def compress_to_gz(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
