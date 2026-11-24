"""CSV-driven execution, requirement traceability and Excel/HTML reporting."""
from pathlib import Path
import csv
import datetime
import html
import json
import time
from collections import Counter
import pandas as pd
from ecommerce_app import fixture, D

ROOT = Path(__file__).resolve().parent


def execute_case(row):
    # 1. Khởi tạo môi trường độc lập cho từng test case qua fixture
    app, user, cart = fixture(row['fixture_key'])
    op = row['operation']

    # Parse dữ liệu đầu vào từ cột input_json
    try:
        inputs = json.loads(row['input_json']) if row.get('input_json') else {}
    except json.JSONDecodeError as e:
        return {
            **row,
            'actual_result': f'JSON_PARSE_ERROR: {e}',
            'error_message': str(e),
            'execution_status': 'BLOCKED',
            'execution_time_ms': 0.0,
            'evidence_reference': 'Invalid input_json format',
            'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    actual_error = ''
    actual = ''
    before_stock = {k: p.stock for k, p in app.catalog.products.items()}
    before_used_codes = set(user.used_codes)
    start_time = time.perf_counter()

    # 2. Thực thi nghiệp vụ (Test Dispatcher)
    try:
        if op == 'get_catalog':
            product = app.catalog.get(inputs['sku'])
            actual = product.title

        elif op == 'cart_add':
            sku = inputs['sku']
            qty = inputs['quantity']
            cart.add(sku, qty)
            # Lấy tổng số lượng hiện tại của SKU trong giỏ hàng
            line = next((x for x in cart.lines if x.sku == sku), None)
            actual = str(line.quantity) if line else '0'

        elif op == 'cart_subtotal':
            sub = cart.subtotal()
            actual = f'{sub:.0f}'

        elif op == 'apply_voucher':
            # Lấy subtotal từ giỏ hàng hiện tại của fixture
            sub = cart.subtotal()
            disc = app.promotions.discount(inputs['code'], sub, user)
            actual = f'{disc:.0f}'

        elif op == 'checkout_cod':
            voucher_code = inputs.get('voucher')
            order = app.place(
                user, cart, area='inner', voucher=voucher_code,
                method='COD', approved=True, key=row['test_case_id']
            )
            actual = order.status

        elif op == 'checkout_declined':
            voucher_code = inputs.get('voucher')
            app.place(
                user, cart, area='inner', voucher=voucher_code,
                method='ONLINE', approved=False, key=row['test_case_id']
            )
            actual = 'NO_ERROR'

        else:
            raise ValueError(f'UNKNOWN_TEST_OPERATION: {op}')

    except ValueError as exc:
        actual_error = str(exc)
        actual = f'ERROR:{actual_error}'
    except Exception as exc:
        # Bắt các lỗi hệ thống không lường trước
        exec_time = round((time.perf_counter() - start_time) * 1000, 3)
        return {
            **row,
            'actual_result': f'UNEXPECTED_EXCEPTION: {type(exc).__name__}',
            'error_message': str(exc),
            'execution_status': 'BLOCKED',
            'execution_time_ms': exec_time,
            'evidence_reference': f'before_codes={list(before_used_codes)}',
            'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    exec_time = round((time.perf_counter() - start_time) * 1000, 3)
    after_stock = {k: p.stock for k, p in app.catalog.products.items()}
    after_used_codes = set(user.used_codes)

    # 3. Kiểm tra kết quả & State (Assertions)
    expectation = str(row['expected_json']).strip()
    expected_err = str(row.get('expected_error', '')).strip()
    assertion_type = row['assertion'].strip()

    if assertion_type == 'equals':
        passed = (actual == expectation)
        if expected_err:
            passed = passed and (actual_error == expected_err)

    elif assertion_type == 'voucher_marked_used':
        # Kiểm tra đơn hàng thành công VÀ mã khuyến mãi đã được ghi nhận vào used_codes
        voucher_code = inputs.get('voucher')
        is_marked = voucher_code in after_used_codes
        actual = 'USED' if is_marked else 'NOT_USED'
        passed = (actual == expectation) and (actual_error == expected_err)

    elif assertion_type == 'voucher_not_used':
        # Kiểm tra giao dịch bị từ chối (PAYMENT_DECLINED) VÀ mã KHÔNG bị ghi nhận vào used_codes
        voucher_code = inputs.get('voucher')
        is_not_marked = voucher_code not in after_used_codes
        actual = 'NOT_USED' if is_not_marked else 'USED'
        passed = (actual == expectation) and (actual_error == expected_err)

    else:
        raise ValueError(f'UNKNOWN_ASSERTION: {assertion_type}')

    evidence = (
        f"stock_before={json.dumps(before_stock)}, stock_after={json.dumps(after_stock)}, "
        f"used_codes_after={list(after_used_codes)}"
    )

    return {
        **row,
        'actual_result': actual,
        'error_message': actual_error,
        'execution_status': 'PASS' if passed else 'FAIL',
        'execution_time_ms': exec_time,
        'evidence_reference': evidence,
        'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


def run_suite(csv_path=None, out_dir=None):
    csv_path = Path(csv_path or ROOT / 'STLab03_Ecommerce_TestCases.csv')
    output = Path(out_dir or ROOT / 'reports')
    output.mkdir(exist_ok=True, parents=True)

    with csv_path.open(newline='', encoding='utf-8-sig') as f:
        testcases = list(csv.DictReader(f))

    # Kiểm tra trùng lặp ID của test case
    ids = [x['test_case_id'] for x in testcases]
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_TEST_IDS')

    results = [execute_case(x) for x in testcases]
    df = pd.DataFrame(results)

    # Tổng hợp kết quả theo Requirement và Trạng thái
    summary = df.groupby(['requirement_id', 'execution_status']).size().unstack(fill_value=0).reset_index()
    counts = Counter(df['execution_status'])
    total_cases = len(df)
    pass_rate = round(100 * counts['PASS'] / total_cases, 1) if total_cases > 0 else 0.0

    totals = pd.DataFrame([{
        'total_cases': total_cases,
        'passed': counts['PASS'],
        'failed': counts['FAIL'],
        'blocked': counts['BLOCKED'],
        'pass_rate_percent': pass_rate
    }])

    # Xuất báo cáo CSV và Excel
    df.to_csv(output / 'test_execution.csv', index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(output / 'test_report.xlsx', engine='openpyxl') as xls:
        df.to_excel(xls, index=False, sheet_name='Execution')
        summary.to_excel(xls, index=False, sheet_name='Traceability')
        totals.to_excel(xls, index=False, sheet_name='Summary')

    # Xuất báo cáo HTML Dashboard
    cols_to_show = ['test_case_id', 'requirement_id', 'scenario_id', 'title', 'expected_json', 'actual_result', 'execution_status']
    rows_html = ''.join(
        '<tr>' + ''.join(
            f'<td class="{str(row.get(k, "")).lower() if k == "execution_status" else ""}">'
            f'{html.escape(str(row.get(k, "")))}</td>'
            for k in cols_to_show
        ) + '</tr>'
        for row in results
    )

    page = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>EduCommerce Test Report</title><style>body {{ font: 15px Arial, sans-serif; margin: 35px; color: #14233c; }}h1, h2 {{ color: #17385f; }}table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}td, th {{ border: 1px solid #cbd5e1; padding: 9px; text-align: left; }}th {{ background: #16385e; color: white; }}tr:nth-child(even) {{ background: #f1f5f9; }}.metric {{ display: inline-block; margin: 10px 12px 20px 0; padding: 14px 20px; border-radius: 10px; background: #edf3f9; font-size: 18px; font-weight: bold; }}.pass {{ color: #16a34a; font-weight: bold; }}.fail {{ color: #dc2626; font-weight: bold; }}.blocked {{ color: #d97706; font-weight: bold; }}</style></head><body><h1>EduCommerce – Automated Test Execution Report</h1><div class="metric">Total: {total_cases}</div><div class="metric" style="color:#16a34a">PASS: {counts["PASS"]}</div><div class="metric" style="color:#dc2626">FAIL: {counts["FAIL"]}</div><div class="metric" style="color:#d97706">BLOCKED: {counts["BLOCKED"]}</div><div class="metric">Pass Rate: {pass_rate}%</div><h2>Traceability & Execution Details</h2><table><tr><th>Case ID</th><th>Requirement</th><th>Scenario</th><th>Title</th><th>Expected</th><th>Actual</th><th>Status</th></tr>{rows_html}</table></body></html>'''
    (output / 'test_dashboard.html').write_text(page, encoding='utf-8')

    print(f'Executed {total_cases} | PASS {counts["PASS"]} | FAIL {counts["FAIL"]} | BLOCKED {counts["BLOCKED"]} | Pass Rate: {pass_rate}%')
    if counts['FAIL'] > 0 or counts['BLOCKED'] > 0:
        print("\n--- NON-PASSING TEST CASES ---")
        print(df.loc[df['execution_status'] != 'PASS', ['test_case_id', 'expected_json', 'actual_result', 'error_message']].to_string(index=False))

    return df, output


if __name__ == '__main__':
    run_suite()
