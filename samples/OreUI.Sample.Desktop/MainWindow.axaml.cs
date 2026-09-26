using Avalonia.Controls;
using Avalonia.Interactivity;

namespace OreUI.Sample;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    public void OpenModal(object? sender, RoutedEventArgs e)
    {
        if (DemoModal is not null)
        {
            DemoModal.IsOpen = true;
        }
    }

    public void CloseModal(object? sender, RoutedEventArgs e)
    {
        if (DemoModal is not null)
        {
            DemoModal.IsOpen = false;
        }
    }
}
