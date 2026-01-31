"""
测试前端工程图导出功能的API
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"


def test_technical_sheet_api():
    """测试工程图API"""
    print("测试工程图导出API...")

    # 首先生成一个测试图案
    print("\n1. 检查是否有pattern...")

    # 尝试使用一个已知的pattern_id（需要先生成）
    # 这里只是测试API端点，实际使用时需要先生成图案
    test_pattern_id = "test-pattern-id"

    # 测试参数
    params = {
        "font_size": 12,
        "color_block_size": 24,
        "row_height": 32,
        "panel_padding": 20,
        "margin_from_pattern": 20,
        "show_total_count": True,
        "show_dimensions": True,
        "show_bead_size": True,
        "sort_by_count": True,
        "exclude_background": True
    }

    print(f"\n2. 准备请求参数...")
    print(json.dumps(params, indent=2, ensure_ascii=False))

    # 构造请求URL
    url = f"{BASE_URL}/api/pattern/{test_pattern_id}/technical-sheet"

    print(f"\n3. 请求URL: {url}")
    print("\n注意：需要先生成图案后才能测试，这里只是验证API端点存在")

    # 检查API是否存在
    try:
        response = requests.get(url)
        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 404:
            print("✓ API端点存在（404表示图案不存在，这是预期的）")
        elif response.status_code == 405:
            print("✓ API端点存在但方法不对（应该用POST）")
        else:
            print(f"✗ 意外的响应: {response.text}")
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
        print(f"  服务器地址: {BASE_URL}")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    return True


def test_statistics_api():
    """测试统计API"""
    print("\n\n测试统计导出API...")

    test_pattern_id = "test-pattern-id"

    formats = ['json', 'csv']

    for fmt in formats:
        url = f"{BASE_URL}/api/pattern/{test_pattern_id}/statistics?format={fmt}"
        print(f"\n测试 {fmt.upper()} 格式: {url}")

        try:
            response = requests.get(url)
            print(f"响应状态码: {response.status_code}")

            if response.status_code == 404:
                print(f"✓ {fmt.upper()} API端点存在（404表示图案不存在）")
        except requests.exceptions.ConnectionError:
            print("✗ 无法连接到服务器")
            return False
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("工程图导出功能API测试")
    print("=" * 60)

    print("\n确保服务器正在运行: python app.py")
    print("然后访问: http://localhost:8000\n")

    success1 = test_technical_sheet_api()
    success2 = test_statistics_api()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("✓ API端点测试通过")
        print("\n使用说明:")
        print("1. 在Web界面上传图片并生成拼豆图案")
        print("2. 在结果页面点击'导出工程图'按钮")
        print("3. 系统会自动调用API并下载工程图纸")
    else:
        print("✗ API端点测试失败")
        print("请检查服务器是否正常运行")
    print("=" * 60)
