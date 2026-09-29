public class PricingEngine {

    public int compute(int amount, int reduction) {
        int finalValue = amount - reduction;

        if (finalValue < 0) {
            return 0;
        }

        return finalValue;
    }
}
