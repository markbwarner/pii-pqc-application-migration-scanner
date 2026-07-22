package com.example.security;

public class PqcWatchlistLabService {

    public String describeExperimentalAlgorithms() {
        String candidateOne = "FrodoKEM";
        String candidateTwo = "Classic McEliece";
        String candidateThree = "BIKE";

        return "Lab validation queue: " + candidateOne + ", " + candidateTwo + ", and " + candidateThree;
    }
}
