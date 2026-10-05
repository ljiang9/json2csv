# json2csv

JSON 对象数组转 CSV/TSV，一行命令搞定。

纯 Python 标准库，离线运行，无依赖。

## 快速开始

```bash
python -m json2csv examples/users.json
```

输出：

```csv
address,age,email,id,name,tags,active
"{""city"": ""上海"", ""zip"": ""200000""}",28,qiang@example.com,1,阿强,"[""vip"", ""早鸟""]",
"{""city"": ""北京"", ""zip"": ""100000""}",25,,2,小红,,
"{""city"": ""广州""}",41,wang@example.com,3,老王,,true
```

注意：`小红` 没有 `email`，对应单元格为空；`tags` 是数组，被编码为 JSON 字符串。

## 用法

| 命令 | 说明 |
|---|---|
| `json2csv users.json` | 转 CSV 输出到 stdout |
| `json2csv users.json --out users.csv` | 写到文件 |
| `json2csv users.json --columns name,email` | 只取这两列，按给定顺序 |
| `json2csv users.json --flatten` | 嵌套对象拍平成 `address.city` 这样的列 |
| `json2csv users.json --no-header` | 不输出表头行 |
| `json2csv users.json --tsv` | 输出 TSV（制表符分隔） |
| `cat users.json \| json2csv --stdin` | 从管道读取 |

`--flatten` 示例：

```csv
address.city,address.zip,age,email,id,name,tags,active
上海,200000,28,qiang@example.com,1,阿强,"[""vip"", ""早鸟""]",
```

## 设计取舍

- **嵌套值默认 JSON 编码**：不加 `--flatten` 时，对象/数组单元格写成紧凑 JSON 字符串——信息不丢失，CSV 仍合法。
- **缺键 → 空单元格**：某行没有某个键，对应位置留空，不报错。
- **列顺序**：默认按"键在所有行中首次出现的顺序"；`--columns` 可显式指定子集与顺序（写错的列名会得到全空列——这是故意的，显式优于猜测）。
- **退出码**：0 成功；1 数据问题（空数组、元素不是对象）；2 用法/IO 错误。

## 已知局限

- 只接受**顶层为数组、元素全为对象**的 JSON；单个对象或其它形状会明确报错，不猜。
- 整个文件读入内存，GB 级 JSON 请先用 `jq` 切片。
- `true`/`false`/`null` 转为 `true`/`false`/空字符串；需要其它映射请提 issue。
- CSV 引号转义遵循 RFC 4180（`csv` 模块默认行为）。
