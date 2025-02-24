import javax.swing.*;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.BasicStroke;

public class Main extends JFrame {
    public Main() {
        setTitle("Graphics");
        setSize(800, 600);
        setVisible(true);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
    }

    public void paint(Graphics g) {
        super.paint(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setStroke(new BasicStroke(5)); // Set the line thickness to 5
        g2.drawLine(250, 200, 550, 200); // horizontal line
        g2.drawLine(550, 200, 600, 280); // right
        g2.drawLine(250, 200, 200, 280); // left
        g2.drawLine(200, 280, 400, 500); // left leg
        g2.drawLine(600, 280, 400, 500); // right leg
    }

    public static void main(String[] args) {
        Main t = new Main();
    }
}
