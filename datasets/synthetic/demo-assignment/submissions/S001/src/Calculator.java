public class Calculator {

    public int calculate(int price, int discount) {
        int result = price - discount;

        if (result < 0) {
            return 0;
        }

        return result;
    }
}
