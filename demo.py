import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "5175"))
DATA_FILE = Path(__file__).with_name("inventory.json")

PAGE = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f3f5f1">
  <title>Kho bãi sỉ lẻ | Nhập xuất kho</title>
  <style>
	:root{font-family:"Avenir Next",Avenir,"Segoe UI",sans-serif;color:#202b25;background:#f3f5f1;font-synthesis:none;--green:#176b50;--dark:#104a39;--line:#e1e7e1;--muted:#77827a;--white:#fff;--orange:#b9532c}
	*{box-sizing:border-box}body{margin:0;min-width:320px}.shell{max-width:1160px;margin:auto;padding:0 28px 48px}.top{height:68px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.brand{display:flex;align-items:center;gap:10px;font-weight:750}.mark{display:grid;place-items:center;width:32px;height:32px;border-radius:8px;color:var(--dark);background:#d8ef79;font-weight:800}.top small{color:var(--muted);font-size:12px}.intro{padding:34px 0 23px}.eyebrow{margin:0 0 8px;color:var(--green);font-size:10px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase}h1{margin:0;font-size:27px;letter-spacing:0}.intro p:last-child{margin:7px 0 0;color:var(--muted);font-size:13px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin-bottom:16px}.stat,.panel{border:1px solid var(--line);border-radius:7px;background:var(--white)}.stat{padding:16px 18px}.stat label{color:var(--muted);font-size:11px}.stat strong{display:block;margin-top:9px;font-size:25px;font-variant-numeric:tabular-nums}.columns{display:grid;grid-template-columns:minmax(280px,.78fr) minmax(0,1.55fr);gap:15px;align-items:start}.panel-head{min-height:59px;padding:14px 17px;border-bottom:1px solid var(--line)}h2{margin:0;font-size:13px}.panel-head p{margin:4px 0 0;color:var(--muted);font-size:10px}.form{display:grid;gap:13px;padding:17px}.field{display:grid;gap:6px;color:#536057;font-size:10px;font-weight:700}.field input,.field select{width:100%;height:39px;padding:0 10px;border:1px solid var(--line);border-radius:5px;color:#202b25;background:#fff;font:inherit;font-size:12px;font-weight:400}.field input:focus,.field select:focus{outline:2px solid #a8cfb5;outline-offset:1px}.submit{height:40px;border:0;border-radius:5px;color:white;background:var(--green);font-size:12px;font-weight:700}.submit:hover{background:var(--dark)}.error{display:none;padding:9px;border-radius:5px;color:#963e20;background:#f9ebe5;font-size:11px}.error.show{display:block}.hint{margin:0;color:var(--muted);font-size:10px;line-height:1.55}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px}.export{padding:7px 10px;border:1px solid var(--line);border-radius:5px;color:var(--green);background:white;font-size:10px;font-weight:700;cursor:pointer}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;white-space:nowrap}th{padding:10px 14px;color:#839087;background:#fafbf9;font-size:9px;letter-spacing:.5px;text-transform:uppercase}td{padding:12px 14px;border-top:1px solid #edf0ed;font-size:11px}.qty{font-weight:700;font-variant-numeric:tabular-nums}.badge{display:inline-block;padding:4px 7px;border-radius:20px;color:var(--green);background:#e8f2ed;font-size:9px;font-weight:700}.badge.low{color:var(--orange);background:#faece5}.empty{text-align:center;color:var(--muted);padding:25px 12px}.history{margin-top:15px}.history td,.history th{padding-left:12px;padding-right:12px}.type-in{color:var(--green);font-weight:700}.type-out{color:var(--orange);font-weight:700}.toast{position:fixed;right:20px;bottom:20px;padding:11px 15px;border-radius:6px;color:#fff;background:var(--dark);font-size:12px;opacity:0;transform:translateY(6px);transition:.18s;pointer-events:none}.toast.show{opacity:1;transform:none}
	@media(max-width:760px){.shell{padding:0 15px 30px}.top{height:56px}.top small{font-size:10px}.intro{padding:25px 0 18px}h1{font-size:23px}.columns{grid-template-columns:1fr}.stats{gap:8px}.stat{padding:13px}.stat strong{font-size:21px}.stat label{font-size:10px}.history{margin-top:12px}}
	@media(max-width:380px){.stats{grid-template-columns:1fr 1fr}.stat:last-child{grid-column:span 2}}
	@media(prefers-reduced-motion:reduce){*{transition:none!important}}
  </style>
</head>
<body>
  <main class="shell">
	<header class="top"><div class="brand"><span class="mark">M</span><span>Kho Mộc</span></div><small id="today"></small></header>
	<section class="intro"><p class="eyebrow">Quản lý kho hàng</p><h1>Nhập xuất kho</h1><p>Theo dõi số lượng hàng hóa và lịch sử giao dịch.</p></section>
	<section class="stats" aria-label="Tổng quan kho">
	  <article class="stat"><label>Mặt hàng</label><strong id="product-count">0</strong></article>
	  <article class="stat"><label>Tổng tồn kho</label><strong id="stock-total">0</strong></article>
	  <article class="stat"><label>Cần nhập thêm</label><strong id="low-count">0</strong></article>
	</section>
	<div class="columns">
	  <section class="panel">
		<div class="panel-head"><h2>Tạo phiếu</h2><p>Ghi nhận hàng nhập hoặc xuất khỏi kho.</p></div>
		<form class="form" id="movement-form">
		  <label class="field">Loại phiếu<select id="movement-type"><option value="in">Nhập kho</option><option value="out">Xuất kho</option></select></label>
		  <label class="field">Tên sản phẩm<input id="product-name" maxlength="80" required placeholder="Ví dụ: Ly sứ men xanh"></label>
		  <label class="field">Số lượng<input id="quantity" type="number" min="1" step="1" required placeholder="Nhập số lượng"></label>
		  <label class="field">Ghi chú<input id="note" maxlength="120" placeholder="Nhà cung cấp, đơn hàng..."></label>
		  <div class="error" id="form-error" role="alert"></div>
		  <button class="submit" type="submit">Lưu phiếu</button>
		  <p class="hint">Phiếu xuất chỉ được ghi nhận khi kho còn đủ số lượng.</p>
		</form>
	  </section>
	  <section class="panel">
		<div class="panel-head toolbar"><div><h2>Tồn kho</h2><p>Số lượng hiện có theo từng mặt hàng.</p></div><button class="export" id="export-stock" type="button">↓ Tải CSV</button></div>
		<div class="table-wrap"><table><thead><tr><th>Sản phẩm</th><th>Tồn kho</th><th>Trạng thái</th></tr></thead><tbody id="stock-rows"></tbody></table></div>
	  </section>
	</div>
	<section class="panel history">
	  <div class="panel-head toolbar"><div><h2>Lịch sử nhập xuất</h2><p>Các giao dịch mới nhất trước.</p></div><button class="export" id="export-history" type="button">↓ Tải CSV</button></div>
	  <div class="table-wrap"><table><thead><tr><th>Loại phiếu</th><th>Sản phẩm</th><th>Số lượng</th><th>Ghi chú</th><th>Thời gian</th></tr></thead><tbody id="history-rows"></tbody></table></div>
	</section>
  </main>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script>
	const numberFormat=new Intl.NumberFormat('vi-VN');
	const safe=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
	let state={products:[],transactions:[]};
	async function load(){const response=await fetch('/api/state');state=await response.json();render();}
	function render(){
	  document.querySelector('#product-count').textContent=numberFormat.format(state.products.length);
	  document.querySelector('#stock-total').textContent=numberFormat.format(state.products.reduce((sum,item)=>sum+item.stock,0));
	  document.querySelector('#low-count').textContent=numberFormat.format(state.products.filter(item=>item.stock<=5).length);
	  document.querySelector('#stock-rows').innerHTML=state.products.length?state.products.map(item=>`<tr><td>${safe(item.name)}</td><td class="qty">${numberFormat.format(item.stock)}</td><td><span class="badge ${item.stock<=5?'low':''}">${item.stock<=5?'Sắp hết':'Đang có'}</span></td></tr>`).join(''):'<tr><td colspan="3" class="empty">Chưa có hàng trong kho. Tạo phiếu nhập để bắt đầu.</td></tr>';
	  document.querySelector('#history-rows').innerHTML=state.transactions.length?state.transactions.map(item=>`<tr><td class="type-${item.type}">${item.type==='in'?'Nhập kho':'Xuất kho'}</td><td>${safe(item.product)}</td><td class="qty">${item.type==='in'?'+':'−'}${numberFormat.format(item.quantity)}</td><td>${safe(item.note||'—')}</td><td>${safe(item.created_at)}</td></tr>`).join(''):'<tr><td colspan="5" class="empty">Chưa có giao dịch.</td></tr>';
	}
	function downloadCsv(filename,rows){const content='\uFEFF'+rows.map(row=>row.map(value=>'"'+String(value??'').replace(/"/g,'""')+'"').join(',')).join('\r\n');const link=document.createElement('a');const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));link.href=url;link.download=filename;link.click();URL.revokeObjectURL(url);}
	document.querySelector('#movement-form').addEventListener('submit',async event=>{
	  event.preventDefault();const error=document.querySelector('#form-error');error.classList.remove('show');
	  const payload={type:document.querySelector('#movement-type').value,product:document.querySelector('#product-name').value.trim(),quantity:Number(document.querySelector('#quantity').value),note:document.querySelector('#note').value.trim()};
	  try{const response=await fetch('/api/transactions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const result=await response.json();if(!response.ok)throw new Error(result.error||'Không thể lưu phiếu.');state=result;render();event.target.reset();document.querySelector('#quantity').value='';const toast=document.querySelector('#toast');toast.textContent='Đã lưu phiếu '+(payload.type==='in'?'nhập.':'xuất.');toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2200);}catch(exception){error.textContent=exception.message;error.classList.add('show');}
	});
	document.querySelector('#export-stock').addEventListener('click',()=>downloadCsv('ton-kho.csv',[['Sản phẩm','Số lượng'],...state.products.map(item=>[item.name,item.stock])]));
	document.querySelector('#export-history').addEventListener('click',()=>downloadCsv('lich-su-nhap-xuat.csv',[['Loại phiếu','Sản phẩm','Số lượng','Ghi chú','Thời gian'],...state.transactions.map(item=>[item.type==='in'?'Nhập kho':'Xuất kho',item.product,item.quantity,item.note,item.created_at])]));
	document.querySelector('#today').textContent=new Intl.DateTimeFormat('vi-VN',{weekday:'short',day:'numeric',month:'short',year:'numeric'}).format(new Date());
	load().catch(()=>{document.querySelector('#form-error').textContent='Không kết nối được máy chủ.';document.querySelector('#form-error').classList.add('show');});
  </script>
</body>
</html>"""


def load_state():
	if not DATA_FILE.exists():
		return {"products": [], "transactions": []}
	try:
		with DATA_FILE.open(encoding="utf-8") as data_file:
			state = json.load(data_file)
		if isinstance(state.get("products"), list) and isinstance(state.get("transactions"), list):
			return state
	except (OSError, json.JSONDecodeError):
		pass
	return {"products": [], "transactions": []}


def save_state(state):
	temporary_file = DATA_FILE.with_suffix(".tmp")
	with temporary_file.open("w", encoding="utf-8") as data_file:
		json.dump(state, data_file, ensure_ascii=False, indent=2)
	temporary_file.replace(DATA_FILE)


class InventoryHandler(BaseHTTPRequestHandler):
	def send_json(self, status, payload):
		body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self):
		if self.path == "/" or self.path == "/index.html":
			body = PAGE.encode("utf-8")
			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=utf-8")
			self.send_header("Content-Length", str(len(body)))
			self.end_headers()
			self.wfile.write(body)
			return
		if self.path == "/api/state":
			self.send_json(200, load_state())
			return
		self.send_json(404, {"error": "Không tìm thấy trang."})

	def do_POST(self):
		if self.path != "/api/transactions":
			self.send_json(404, {"error": "Không tìm thấy địa chỉ."})
			return
		try:
			length = int(self.headers.get("Content-Length", "0"))
			if length < 1 or length > 16_384:
				raise ValueError("Dữ liệu gửi lên không hợp lệ.")
			payload = json.loads(self.rfile.read(length))
			movement_type = payload.get("type")
			product_name = str(payload.get("product", "")).strip()
			quantity = payload.get("quantity")
			note = str(payload.get("note", "")).strip()[:120]
			if movement_type not in ("in", "out"):
				raise ValueError("Vui lòng chọn loại phiếu hợp lệ.")
			if not product_name or len(product_name) > 80:
				raise ValueError("Tên sản phẩm cần từ 1 đến 80 ký tự.")
			if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
				raise ValueError("Số lượng phải là số nguyên lớn hơn 0.")
		except (ValueError, TypeError, json.JSONDecodeError) as error:
			self.send_json(400, {"error": str(error)})
			return

		state = load_state()
		product = next((item for item in state["products"] if item["name"].casefold() == product_name.casefold()), None)
		if movement_type == "out" and product is None:
			self.send_json(400, {"error": "Sản phẩm chưa có trong kho. Hãy tạo phiếu nhập trước."})
			return
		if movement_type == "out" and quantity > product["stock"]:
			self.send_json(400, {"error": f"Không đủ tồn kho. Hiện còn {product['stock']} sản phẩm."})
			return
		if product is None:
			product = {"id": uuid4().hex, "name": product_name, "stock": 0}
			state["products"].append(product)
		product["stock"] += quantity if movement_type == "in" else -quantity
		state["transactions"].insert(0, {
			"id": uuid4().hex,
			"type": movement_type,
			"product": product["name"],
			"quantity": quantity,
			"note": note,
			"created_at": datetime.now().astimezone().strftime("%d/%m/%Y %H:%M"),
		})
		try:
			save_state(state)
		except OSError:
			self.send_json(500, {"error": "Không lưu được dữ liệu kho vào file."})
			return
		self.send_json(200, state)

	def log_message(self, format_string, *args):
		print(f"{self.log_date_time_string()} - {format_string % args}")


if __name__ == "__main__":
	server = ThreadingHTTPServer((HOST, PORT), InventoryHandler)
	print(f"Web nhập xuất đang chạy tại http://localhost:{PORT}")
	print("Nhấn Ctrl+C để dừng máy chủ.")
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nĐã dừng máy chủ.")
	finally:
		server.server_close()
