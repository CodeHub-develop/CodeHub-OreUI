using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

namespace OreUI.Sample;

public partial class MainWindow : Window
{
    private static readonly string[] NavSections = new[]
    {
        "辅助功能", "操作指南", "游戏", "多人游戏", "键盘与鼠标", "控制器", "触控", "个人资料"
    };

    public MainWindow()
    {
        AvaloniaXamlLoader.Load(this);
    }

    /// <summary>左侧导航行点击：单选高亮，并更新右侧标题与面包屑。</summary>
    public void NavRow_Click(object? sender, RoutedEventArgs e)
    {
        if (sender is not Button btn)
        {
            return;
        }

        foreach (var nav in new[]
                 {
                     NavAccessibility, NavHowToPlay, NavGame, NavMultiplayer,
                     NavKeyboard, NavController, NavTouch, NavProfile
                 })
        {
            if (nav is not null)
            {
                nav.Classes.Set("selected", ReferenceEquals(nav, btn));
            }
        }

        var title = (btn.Content as StackPanel)?.Children
            .OfType<TextBlock>().LastOrDefault()?.Text ?? "设置";
        if (SectionTitle is not null)
        {
            SectionTitle.Text = title + "设置";
        }
        if (HeaderCrumb is not null)
        {
            HeaderCrumb.Text = title;
        }
    }

    public void RenderDistance_Changed(object? sender, RangeBaseValueChangedEventArgs e)
    {
        if (RenderDistanceText is not null)
        {
            RenderDistanceText.Text = $"{(int)e.NewValue} chunks";
        }
    }

    public void SimulationDistance_Changed(object? sender, RangeBaseValueChangedEventArgs e)
    {
        if (SimulationDistanceText is not null)
        {
            SimulationDistanceText.Text = $"{(int)e.NewValue} chunks";
        }
    }

    public void OpenModal(object? sender, RoutedEventArgs e)
    {
        if (ModalOverlay is not null)
        {
            ModalOverlay.IsVisible = true;
        }
    }

    public void CloseModal(object? sender, RoutedEventArgs e)
    {
        if (ModalOverlay is not null)
        {
            ModalOverlay.IsVisible = false;
        }
    }
}
