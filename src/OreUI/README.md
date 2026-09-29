# CodeHub-OreUI

<img width="562" height="322" alt="oreui_contact_sheet" src="https://raw.githubusercontent.com/Hub-code-develop/CodeHub-OreUI/main/src/OreUI/Assets/oreui_contact_sheet.png" />

Minecraft 基岩版（Bedrock Edition）**OreUI** 风格的 **Avalonia 12** 控件库。

提供一套贴近基岩版设置的视觉与交互规范：面板、按钮（hero / primary / secondary / destructive / default 变体）、开关、复选、单选、滑块、输入框、下拉、标签（Tag）、旋转环（Spinner）、进度条、选择列表（SelectionList）、菜单行（MenuRow）、标签页（TabControl）与模态（Modal）等。

> 所有原生控件都通过 `.ore` 门控类接入 OreUI 主题，自定义控件（`OrePanel` / `OreDivider` / `OreHeader` / `OreTag` / `OreSpinner` / `OreMenuRow` / `OreSelectionList` / `OreModal`）则自带类型化 `ControlTheme`，开箱即用。

## 安装

```bash
dotnet add package CodeHub-OreUI
```

## 使用

在 `App.axaml` 的 `<Application.Styles>` 中引入 OreUI 主题（需放在 `FluentTheme` 之后）：

```xml
<Application.Styles>
  <FluentTheme />
  <StyleInclude Source="avares://OreUI/Themes/OreUITheme.axaml" />
</Application.Styles>
```

### 原生控件加 `.ore` 类

```xml
<Button Classes="ore hero" Content="开始游戏" />
<ToggleSwitch Classes="ore" Content="启用实验性玩法" IsChecked="True" />
<Slider Classes="ore" Width="240" />
<TextBox Classes="ore" Width="340" PlaceholderText="输入世界名称..." />
<ComboBox Classes="ore" Width="240" />
```

### 自定义控件

```xml
<ore:OrePanel>
  <ore:OreHeader Title="设置" ShowBack="True" />
  <ore:OreDivider Classes="horizontal" />
  <ore:OreTag TagVariant="Success" Content="已连接" />
  <ore:OreSpinner />
  <ore:OreSelectionList>
    <ore:OreMenuRow Icon="&#xe600;" Subtitle="存档管理" ShowChevron="True" />
  </ore:OreSelectionList>
</ore:OrePanel>
```

## 目标框架

`net8.0` 与 `net10.0`，依赖 `Avalonia` 12.0.0。

## 许可

MIT © CodeHub
