# ascii-render 一键脚本

一行命令在任意平台下载并运行 ascii-render。

## 使用方法

### Linux / macOS / WSL

```bash
# 默认示例（爱你.gif）
bash <(curl -sL https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.sh)

# 指定输入
bash <(curl -sL https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.sh) /path/to/image.gif
```

### Windows (PowerShell)

```powershell
# 默认示例（爱你.gif）
irm https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.ps1 | iex

# 指定输入
$img = "https://example.com/love.gif"
irm https://raw.githubusercontent.com/looyun/ascii-render/master/scripts/demo.ps1 | iex -Img $img
```


## 注意事项

- 首次运行会自动下载对应平台的二进制文件
- 临时文件会在执行结束后自动清理
- 需要网络连接以下载二进制和素材
