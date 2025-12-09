---
title: "A/B Test Analysis: Progression Gate Impact in Cookie Cats"
description: "A complete walkthrough of designing, running, and interpreting an A/B test to optimize progression gate placement in the mobile game Cookie Cats."
date: 2025-6-09
draft: false
author: "Jiaqi Yang"
technologies:
  - A/B Testing
  - Game Analytics
  - Retention Analysis
  - Mobile Games
status: Completed
github: "https://github.com/example/demo-ml"
image: "@/assets/blog/cookiecats-abtest.jpg"
---


# Background

This project is to conduct AB Test on game **Cookie Cats**, a captivating puzzle game developed by Tactile Entertainment for mobile platform. This game belongs to the *match-3* puzzle genre, where players link cookies of identical colors to complete level objectives.

## What is our current problem?

In our current live version, we face two pressing challenges:

- **User engagement**:after the initial onboarding, some players lose interest and daily activity declines. Specifically, our Day-7 retention rate and **DAU** (Daily Active Users) have been trending downward, signaling that engagement has weakened.
- **Conversion rate**: although progression gates create monetization opportunities, the proportion of players choosing to make in-app purchases remains below expectations.

As a result, we need to carefully re-examine the placement of progression gates in order to **boost player activity and increase conversion without negatively affecting retention**.

## What can we do?

To prevent players from rushing through the game too quickly, developers introduced *progression gates*. At these gates, players must either wait a certain amount of time or make an **in-app purchase** to continue immediately.

- This mechanic **paces the gameplay**, preventing fatigue and overconsumption.
- It **increases retention**, as players are encouraged to return after waiting.
- It **creates monetization opportunities**, since impatient players may choose to pay.

However, progression gates must be carefully placed.

- **Too early**: players may feel frustrated and quit before becoming invested.
- **Too late**: the mechanic loses its effectiveness as a retention and monetization tool.



## Why Use AB Test?

### Other Games using AB Test

经典案例

### Why use A/B Test?

A/B testing is an essential method to evaluate the impact of different game design choices while minimizing risk to the player base. Instead of applying a change to all players at once, the population is divided into groups:
	•	Control group (A): experiences the original version of the game.
	•	Treatment group (B): experiences the modified version, such as a different progression gate placement.

This approach ensures that only a **subset** of players is exposed to a potential negative change. If the treatment group shows lower retention or higher churn, developers can roll back the change without disrupting the entire player community.

In addition, A/B testing enables developers to:
	•	Quantify trade-offs between engagement and monetization.
	•	Detect unintended consequences early, such as players abandoning the game due to frustration.
	•	Base decisions on evidence rather than assumptions, ensuring design choices are data-driven.

By carefully controlling who experiences which version, A/B testing provides a safe and reliable way to optimize progression gate placement with minimal disruption to the overall player experience.



## **Experiment Design**

​	![flowmap](/Users/codingleo/Downloads/flowmap.png)

To conduct A/B Test, we need to 

- `userid`: The id of user to distinguish different users.
- `version`: We seperated the users to two groups with different game versions.
- ```sum_gamerounds```: total number of game rounds played in the first 14 days 
- ```retention_1```: whether the user returned on Day 1. True or False
- ```retention_7```, whether the user returned on Day 7.True or False

These variables allow us to measure both **short-term engagement** (retention) and **overall activity** (game rounds), forming the basis for hypothesis testing.

1. **Hypothesis**

   We had **90,189 players**, randomly assigned to two groups to validate our assumption: 

   - **Later gate placement**: Expected to reduce early churn and improve retention, but may delay or decrease monetization opportunities.
   - **Earlier gate placement**: May encourage earlier in-app purchases, but risks higher churn as some players could feel blocked too soon.

   

2. **Groups**

   Players were divided into two groups using a **hash-based randomization method** on `userid`. This ensures that assignment is both **random** and **deterministic**, preventing any manual bias while guaranteeing reproducibility.

   > We used `mmh3.hash % 100` to compute a `mapped_id` and then assign players into buckets, which can map `userid` to $$[0,99]$$. As a result we can get: 
   >
   > - `mapped_id < 50` were mapped to the **Control group (A)**
   > - `mapped_id ≥ 50`  were mapped to the **Treatment group (B)
   >
   > We also conducted **Chi Square Test** to ensure the groups are statistically comparable to the expected allocation

   Then we can change the position of progression gate:

   - **Control group (A)**: Progression gate introduced at the current baseline (**Level 30**).
   - **Treatment group (B)**: Progression gate shifted to a later point (**Level 40**).

   Each group contained approximately **45,000 players**, resulting in statistically comparable sample sizes. By using hashing, we minimize the risk of hidden imbalances (e.g., player skill level, geographic distribution, or device type) that could otherwise bias results.

   Special care was taken to address potential issues like **Simpson’s Paradox**, where aggregated results may hide or reverse trends present in subgroups. To mitigate this, we verified that key baseline characteristics (such as average play rounds and Day-0 activity) were balanced across both groups prior to analysis.

   

   

3. **Metrics**

In collaboration with the business team, we agreed to focus on **Day-1** and **Day-7 retention rates** as the **primary metrics** of this experiment.

- While monetization metrics (e.g., conversion rate, purchase rate, ARPU) are highly relevant to the business, they typically require a longer observation window and are influenced by multiple factors beyond progression gate placement.
- Retention, on the other hand, provides a more **direct and immediate signal** of user engagement. Early churn is one of the strongest predictors of long-term player value, and thus retention serves as a reliable proxy for evaluating design changes in the short term.

Specifically:

- **Day-1 retention** reflects the effectiveness of onboarding and early game experience.
- **Day-7 retention** captures medium-term engagement, showing whether players continue to find value beyond the initial novelty.

Although secondary indicators such as **user growth rate**, **total play sessions**, or **early monetization patterns** were considered, the decision was made to prioritize retention as the most **actionable and timely metric** for this test phase.



4. **Duration & Sample Size**

We also need to find a good duration for A/B Test. The time period should be long enough to reach statistical significance. If the time period is too short, only very active users can be envolved into the test. 

Because we are doing test for a mobile game, we may need to ensure the period contain whole weeks to avoid the impact of working time.     





# A/B Test Process

## Data Preprocessing

### Outlier Detection and Treatment

To start A/B Test, we need to check the data and remove candidate outliers. We first use histogram and box gram to check the distribution of `sum_gamerounds`:

![image-20250929015715036](/Users/codingleo/Library/Application Support/typora-user-images/image-20250929015715036.png)

From the plots, we observe one extreme outlier: a user with nearly 50,000 game rounds, which is orders of magnitude higher than the rest of the population. Such a point is very likely due to data error or abnormal behavior, and retaining it would distort both the mean and variance, inflating test statistics.

Therefore, we treat this data point as an outlier and remove it from the dataset:

![image-20250929020403356](/Users/codingleo/Library/Application Support/typora-user-images/image-20250929020403356.png)

After removal, the distribution of sum_gamerounds becomes more representative of the general player population, making the subsequent hypothesis testing more reliable.



And at the same time, some users may only donwload our game but never play it. We should not take these users into account. So we need to have a view of `sum_gameround` against `num_users` :

![image-20250929020642531](/Users/codingleo/Library/Application Support/typora-user-images/image-20250929020642531.png) 

And we can count the number of 0 round players:

```python
ab.groupby("sum_gamerounds")['userid'].count().reset_index(name = 'user_cnt').sort_values('user_cnt', ascending=False)[:20]
```

It turns out that we have 3994 0 round users and we should remove them.

### **Retention Overview**

#### Normality Test

##### Why do we check for normality?

Checking whether the data follows a normal distribution is important because many statistical methods (such as the t-test) rely on the assumption of normality to ensure accuracy and reliability. Normality testing helps us verify whether the chosen statistical method is appropriate for the data, thereby avoiding misleading or incorrect conclusions in hypothesis testing.

If the data is approximately normal, we can apply parametric methods (e.g., the t-test) to test hypotheses, which provide more precise estimates of population parameters (such as the population mean). On the other hand, if the data significantly deviates from normality, using parametric methods may introduce bias or lead to invalid results.

In A/B testing, normality checks are commonly performed to ensure that the statistical tests we apply are valid and trustworthy. 

If the data does not follow a normal distribution, we can instead use non-parametric methods (such as the Mann–Whitney U test), which make fewer assumptions about the underlying distribution and are more flexible across different data types.

|                             | **Non-parametric Test**                                      | **Parametric Test**                                          |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Population Distribution** | Unknown or non-normal distribution                           | Population follows a normal distribution                     |
| **Equal Variance**          | Not required                                                 | Involves two or more populations with equal variances        |
| **Variable Type**           | Ordinal variables, or interval variables that do not follow a normal distribution | Interval or ratio variables                                  |
| **Statistical Power**       | Relatively lower                                             | Relatively higher                                            |
| **Advantages**              | 1. Requires fewer assumptions, more practical, simple to compute, and applicable to a wide range of variables;<br>2. Can be used when parametric test assumptions are not met. | 1. Provides higher statistical validity, allowing more accurate measurement of differences and relationships;<br>2. More powerful than non-parametric tests, and can still be applied even when population distribution is not clearly defined. |
| **Disadvantages**           | 1. Statistical power is generally lower compared to parametric tests;<br>2. Loose assumptions may introduce larger errors in observing parameter differences or relationships. | 1. Requires the assumption of normality, thus has a narrower scope of application;<br>2. Effectiveness and applicability are limited if the assumption of normal distribution is not satisfied. |

This time, we choose **t-test**. We choose to use built-in t-test method from  `scipy` . 

#### Comparing t-test and z-test

| Dimension         | **t-test**                                                   | **z-test**                                                   |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Features**      | - Used when the **population variance is unknown**.<br>- Based on the **t-distribution** (heavier tails).<br>- More suitable for **small or moderate samples (n < 30)**. | - Requires **known population variance (σ²)**.<br>- Based on the **standard normal distribution (z-distribution)**.<br>- More reliable with **large samples (n ≥ 30)**. |
| **Practical Use** | - Widely used in real-world experiments (A/B tests, clinical trials).<br>- Only requires sample mean and sample standard deviation.<br>- Works well when population variance is difficult to estimate. | - Rarely used in practice, since population variance is almost never known.<br>- Mostly seen in theoretical statistics or large-scale survey cases. |
| **Cost**          | - Lower cost: does not require prior knowledge of population variance.<br>- Computationally efficient, applicable in most research scenarios. | - Higher cost: requires population variance, which usually needs additional data collection or external assumptions.<br>- Less efficient when such information is unavailable. |

###### Conclusion

In practice, the **t-test is preferred** because the population variance is typically unknown and difficult to obtain.  

- For small or moderate samples, the t-distribution provides a more accurate inference.  
- Even for large samples, the t-test approximates the z-test closely (since the t-distribution converges to the normal distribution as n → ∞).  
  Therefore, using the t-test is both **practical and cost-effective**, while still maintaining statistical validity.






#### **Game Rounds Played**(Numerical)

Now, we can compared **Day-1** and **Day-7** retention rates between the two groups:

|  version  | count | median  |  mean   |   std    | max  |
| :-------: | :---: | :-----: | :-----: | :------: | :--: |
| `gate_30` | 44699 | 17.0000 | 51.3421 | 102.0576 | 2961 |
| `gate_40` | 45489 | 16.0000 | 51.2988 | 103.2944 | 2640 |

And we can compute the retention rate on **Day-1** and **Day-7**:

|       | RET1_COUNT | RET1_RATIO | RET7_COUNT | RET7_RATIO |
| :---: | :--------: | :--------: | :--------: | :--------: |
| False |   50035    |   0.5548   |   73408    |   0.8139   |
| True  |   40153    |   0.4452   |   16780    |   0.1861   |

![image-20250929022951452](/Users/codingleo/Library/Application Support/typora-user-images/image-20250929022951452.png)

We can find:

1. 55% users did not play our game on **Day-1**;
2. 81% users did not play our game on **Day-7**.

As a result, besides the position of progression gate, we also need to report to other teams that we may need multiple actions to keep users' engagement, e.g. sending some little gifts to help users to finish levels.



Also, we can find that the change of return on Day-1 and Day-7 may also matter. We can create a new field `NewRetentation` to montior it:

| Index | NewRetention | version | count |  median  |   mean   |   std    | max  |
| ----- | :----------: | :-----: | :---: | :------: | :------: | :------: | :--: |
| 0     | False-False  | gate_30 | 22840 |  6.0000  | 11.8197  | 21.6426  | 981  |
| 1     | False-False  | gate_40 | 23597 |  6.0000  | 11.9133  | 20.9010  | 547  |
| 2     |  False-True  | gate_30 | 1825  | 43.0000  | 73.1693  | 93.2223  | 1072 |
| 3     |  False-True  | gate_40 | 1773  | 47.0000  | 75.2611  | 94.4780  | 1241 |
| 4     |  True-False  | gate_30 | 13358 | 33.0000  | 49.6945  | 58.1254  | 918  |
| 5     |  True-False  | gate_40 | 13613 | 32.0000  | 50.0255  | 60.9246  | 2640 |
| 6     |  True-True   | gate_30 | 6676  | 127.0000 | 183.8863 | 189.6264 | 2961 |

To assess whether delaying the first gate changed user engagement, we tested for differences in sum_gamerounds between the two groups. We set the significance level at $\alpha = 0.05$ and formulated the hypotheses as follows:

$$
H_0: \mu_A = \mu_B \quad \text{(no significant difference between groups)}
$$

$$
H_1: \mu_A \neq \mu_B \quad \text{(a significant difference exists between groups)}
$$


![image-20250929023807558](/Users/codingleo/Library/Application Support/typora-user-images/image-20250929023807558.png)

And we can get the following results:

| Field           | Value               |
| --------------- | ------------------- |
| p-value         | 0.509               |
| Mean Difference | -0.0433             |
| Effect Size     | -0.0004             |
| Observed Power  | 0.0505              |
| Conclusion      | Cannot Reject `H_0` |

##### Conclusion

Based on ... 

But ... so **bootstrap**



#### Retention Rates (Binary Metrics)

We analyzed **Day-1** and **Day-7 retention rates** using **two-proportion z-tests**, which evaluate whether the proportion of retained users differs significantly between the control (**gate_30**) and treatment (**gate_40**) groups.

Because we are dealing with binary metrics, we are using **z-test** to validate normality. 

##### Why z-test instead of t-test for proportion metrics?

1. **Nature of the Data**
   - Proportion metrics (e.g., conversion rate, retention rate) are based on **binary outcomes** (success/failure).
   - The underlying distribution is **binomial**, not continuous like a normal distribution of raw values.
   - When the sample size is large, by the Central Limit Theorem, the sample proportion $\hat{p}$ follows an **approximate normal distribution**.

2. **Known Variance Structure**
   - For proportions, the variance can be **directly estimated** as $p(1-p)/n$, where $p$ is the proportion and $n$ is the sample size.
   - Since this variance structure is derived from the binomial model, we do **not need to estimate an unknown population variance** like in the t-test.
   - This makes the z-test appropriate because the standard error is analytically defined.

3. **t-test vs. z-test Context**
   - **t-test** is designed for comparing means of continuous variables when the **population variance is unknown** and must be estimated from the sample.
   - **z-test** is used when the variance (or its exact form) is **known or can be derived**, which is the case for binomially distributed proportions.

4. **Practical Implication in A/B Testing**
   - For conversion rates or retention rates, we can directly compute the pooled variance from observed data.
   - With large sample sizes (typical in A/B testing), the normal approximation holds well, making the z-test both efficient and accurate.
   - Therefore, the z-test is the standard approach for testing differences between two proportions.

##### Z-Test Results

| Metric    | Retention (gate_30) | Retention (gate_40) | p-value | Conclusion                    |
| --------- | ------------------- | ------------------- | ------- | ----------------------------- |
| **Day-1** | 44.8%               | 44.2%               | 0.0739  | ❌ Not significant             |
| **Day-7** | 19.0%               | 18.2%               | 0.0016  | ✅ Significant (gate_40 worse) |



###  Bootstrapping

In A/B testing, a z-test is commonly used to compare two proportions (e.g., conversion rate, retention rate) because the binomial distribution of proportions can be approximated by the normal distribution when the sample size is sufficiently large. The z-test provides a fast and theoretically grounded way to evaluate whether the difference between two groups is statistically significant.

However, relying solely on the z-test has limitations:

1. **Assumption Dependence**  
   - The z-test assumes large sample sizes and that the sampling distribution of proportions is well-approximated by a normal distribution.  
   - When the sample size is small or the proportions are close to 0 or 1, these assumptions may not hold, which can lead to inaccurate p-values and confidence intervals.

2. **Sampling Variability**  
   - A single sample may not fully capture the variability of the population.  
   - Bootstrapping, by repeatedly resampling with replacement, generates an empirical distribution of the statistic (e.g., difference in retention rates). This helps us better understand the random error and variability inherent in our data.

3. **More Reliable Confidence Intervals**  
   - Bootstrapping provides confidence intervals directly from the resampled distributions, without depending on the normal approximation.  
   - These intervals can reveal whether the z-test result is robust or sensitive to its assumptions.

4. **Robustness Check**  
   - By comparing the z-test result with the bootstrap distribution, we can validate the reliability of our findings.  
   - If both methods lead to consistent conclusions, the evidence is stronger.  
   - If results differ, bootstrapping highlights the limitations of the z-test and suggests that caution is needed in interpreting the outcome.



Even after completing a z-test, performing bootstrapping is valuable. It does not replace the z-test but complements it, providing a distribution-free validation of statistical inference. This dual approach increases the robustness, credibility, and interpretability of A/B test conclusions.



##### Process

To conduct bootstrap, we need to follow the following steps:

1. **Sample Data**:  
   Start with an original dataset, usually the observed real-world data.  
   For example, retention rate data for two groups of players in the Cookie Cats game.

2. **Resampling**:  
   Repeatedly draw samples with replacement from the original dataset to create multiple bootstrap samples.  
   Each bootstrap sample is the same size as the original dataset but differs due to randomness.

3. **Compute Statistics of Interest**:  
   For each bootstrap sample, calculate the statistic we care about — e.g., the difference in retention rates (Delta) or other performance metrics.

4. **Evaluate the Quality of Inference**:  
   By observing the distribution of statistics across many bootstrap samples, we can assess the reliability and accuracy of our inference.  
   This helps quantify whether the conclusions drawn from our sample data are trustworthy.


##### Detailed Steps

1. **Create 500 Bootstrap Samples**  
   - Use the bootstrap method to generate 500 resampled datasets from the original data.  
   - Each sample should have the same number of observations as the original dataset.

2. **Calculate Day-1 and Day-7 Retention for Groups A and B**  
   - For each bootstrap sample, calculate the Day-1 and Day-7 retention rates for Group A and Group B after passing certain game levels (e.g., after Level 30 or Level 40).

3. **Plot Bootstrap Distributions**  
   - For each retention rate (Day-1 and Day-7), plot the bootstrap distributions for both Group A and Group B.  
   - These visualizations help illustrate how retention rates vary under different gate placements.

4. **Calculate Retention Differences Between A and B**  
   - For each bootstrap sample, compute the difference in retention rates between Group A and Group B.  
   - This can be summarized by comparing means or medians of the bootstrap samples.

5. **Estimate the Probability of Higher Retention at Level 30**  
   - Determine the probability that Day-1 and Day-7 retention rates are higher when the progression gate is placed at Level 30 versus Level 40.  
   - This can be achieved by comparing the probability mass of the two bootstrap distributions.

6. **Interpret Results and Provide Recommendations**  
   - Based on the analysis and probability estimates, evaluate the effect of placing the first progression gate at Level 30.  
   - Provide recommendations for whether the new gate setting should be kept or reverted.



So we can get the bootstrap data frame:

| index | version | retention_1 | retention_7 |
| :---: | :-----: | :---------: | :---------: |
|   0   |    A    |   0.4478    |   0.1894    |
|   1   |    B    |   0.4418    |   0.1823    |
|   0   |    A    |   0.4466    |   0.1929    |
|   1   |    B    |   0.4444    |   0.1846    |



Then we can plot the distribution:

![image-20251002004305072](/Users/codingleo/Library/Application Support/typora-user-images/image-20251002004305072.png)

Bootstrapping shows that across repeated resampling, **Group A consistently outperforms Group B** in both Day-1 and Day-7 retention.  The distribution shows the shape and overlap intuitively, but it does not give a precise threshold for statistical significance.  

Now we need the **confidence interval** to quantifies the uncertainty and allow us to give the final decision.

We set:
- $$\alpha =0.05$$ 
-  $$lower~ci$$ :  $$\alpha / 2 → 0.025$$
-  $$upper~ci$$ : $$1-\alpha / 2 → 0.975$$

Now we can  create FacetGrid with seaborn:

![image-20251002005907824](/Users/codingleo/Library/Application Support/typora-user-images/image-20251002005907824.png)

Because 0 falls in Day-1 confidence interval we can't say there is significant difference between variant groups.  So we can say:

1. Retention 1-day difference is not significant. 
2. Retention 7-day difference is significant.



# Conclusion

Based on the experimental results, we conducted a non-parametric test to evaluate the impact of moving the first progression gate in the Cookie Cats game from Level 30 to Level 40 on player retention and gameplay rounds.

**Numerical Metric (Game Rounds):**  
Under a two-sided hypothesis test, we obtained a p-value of 0.0509. Given the conventional significance level of α = 0.05, we fail to reject the null hypothesis. This indicates that we do not have sufficient evidence to conclude that there is a significant difference in gameplay rounds between Groups A and B.

**Ratio Metrics (Retention):**  
Using the Bootstrap method, we assessed the stability of retention differences and calculated confidence intervals through resampling. The results are as follows:  
- **Day-1 Retention:** 95% CI = [-0.002, 0.012]. Since the interval includes 0, the difference is not statistically significant.  
- **Day-7 Retention:** 95% CI = [0.008, 0.022]. As the interval does not include 0, the difference is statistically significant.

**Final Conclusion:**  
- **Day-1 Retention:** No significant difference between the experimental and control groups, suggesting that moving the progression gate from Level 30 to Level 40 has no short-term impact on Day-1 retention.  
- **Day-7 Retention:** A significant difference was observed between the experimental and control groups, indicating that the adjustment of the progression gate positively impacts long-term retention.  

Taken together, the experimental results suggest that moving the first progression gate from Level 30 to Level 40 does not significantly affect gameplay rounds or short-term retention but does improve long-term retention. This implies that player experience in the short run is unaffected, while sustained engagement may benefit from the adjustment.








