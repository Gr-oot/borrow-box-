# Borrow Box — Kiro Instructions

## 1. Overview

This document contains the instructions and requirements used to guide **Kiro** during the development of the Borrow Box frontend.

Borrow Box is a rental platform where users can find and rent products according to their needs. One of the main features of the platform is the **AI Rental Assistant**, which helps users find suitable products through a personalized survey.

Kiro was used to assist with creating and structuring parts of the frontend according to the requirements of the Borrow Box project.

---

## 2. Project Context

The frontend should represent a modern and user-friendly rental platform.

The application should allow users to:

* Explore available rental products.
* View product information.
* Understand the rental process.
* Interact with the AI Rental Assistant.
* Answer questions through the AI survey.
* Receive personalized product recommendations.
* Select a product for rental.

The frontend should be designed so that users can easily understand and navigate the platform.

---

## 3. Kiro Development Instructions

The following requirements were used while developing the frontend with Kiro.

### 3.1 General UI Requirements

Create a clean, modern, and responsive interface for the Borrow Box rental platform.

The interface should:

* Be simple and easy to understand.
* Use clear navigation.
* Provide a consistent layout across pages.
* Clearly display important product information.
* Make the rental process easy to follow.
* Provide a clear entry point for the AI Rental Assistant.
* Work across different screen sizes.

---

## 4. Homepage Requirements

The homepage should introduce users to Borrow Box and explain the purpose of the platform.

The homepage should include:

* Borrow Box branding.
* Navigation menu.
* Hero section.
* Short explanation of the rental service.
* Call-to-action for browsing products.
* Call-to-action for the AI Rental Assistant.
* Featured or recommended products.
* Explanation of the benefits of renting.
* Footer section.

The AI Rental Assistant should be prominently accessible from the homepage.

---

## 5. Product Page Requirements

The product section should allow users to browse available rental products.

Each product should display relevant information such as:

* Product name.
* Product image.
* Product category.
* Product description.
* Important features.
* Rental price.
* Availability.
* Rental-related information.
* Option to select or rent the product.

The design should make it easy for users to compare different products.

---

## 6. AI Rental Assistant Requirements

The AI Rental Assistant is one of the most important features of Borrow Box.

The frontend should provide an interactive interface where users can communicate with the assistant.

The assistant should guide the user through a survey.

### Example Survey Flow

```text
Start AI Assistant
        ↓
Ask User Questions
        ↓
Collect Answers
        ↓
Show Progress
        ↓
Complete Survey
        ↓
Display Recommendation
```

The survey interface should be simple and should not overwhelm the user.

---

## 7. AI Survey Questions

The frontend should support questions that help understand the user's rental requirements.

Possible questions include:

* What do you need the product for?
* Which category are you interested in?
* How long do you need the product?
* What is your budget?
* Which features are important to you?
* Do you have any specific preferences?

The interface should allow users to easily provide their answers.

---

## 8. Recommendation Screen

After the survey is completed, the frontend should display the AI-generated recommendation.

The recommendation screen should contain:

* Recommended product.
* Product image.
* Product name.
* Key features.
* Rental price.
* Reason for recommendation.
* Availability.
* Option to rent the product.
* Option to view other suitable products.

The recommendation should be presented clearly so the user understands why the product was selected.

---

## 9. Navigation Requirements

The navigation should make it easy for users to move between the major areas of Borrow Box.

Possible navigation items include:

```text
Home
Products
AI Rental Assistant
About
Login / Sign Up
```

The navigation should remain consistent throughout the application.

---

## 10. Responsive Design

The frontend should be responsive and usable on:

* Desktop computers.
* Laptops.
* Tablets.
* Mobile phones.

The layout should automatically adapt to different screen sizes.

Important elements such as navigation, product cards, buttons, forms, and the AI Assistant should remain accessible on smaller screens.

---

## 11. User Experience Requirements

The frontend should focus on providing a simple and intuitive user experience.

The user should be able to:

1. Understand what Borrow Box does.
2. Find available products.
3. Start the AI Rental Assistant.
4. Complete the survey easily.
5. Understand the recommendation.
6. Select a product.
7. Continue with the rental process.

The number of unnecessary steps should be minimized.

---

## 12. Component Structure

The frontend should be organized into reusable components where appropriate.

Potential components include:

```text
Navbar
HeroSection
ProductCard
ProductList
ProductDetails
AIRentalAssistant
SurveyQuestion
ProgressIndicator
RecommendationCard
RentalButton
Footer
```

Reusable components should be preferred over duplicating similar UI elements.

---

## 13. Backend Integration Considerations

The frontend should be structured so that it can communicate with the Borrow Box backend.

The application is planned to use:

* **Python**
* **Node.js**
* **MySQL**

The frontend should be prepared to receive product information, availability information, user requirements, and AI recommendations from the backend.

The frontend should not assume that product information is permanently hardcoded if it will eventually be provided by the backend/database.

---

## 14. AI Assistant Integration Considerations

The AI Rental Assistant frontend should be designed so that the survey responses can be sent to the backend/AI system.

The intended flow is:

```text
Frontend Survey
      ↓
User Responses
      ↓
Backend
      ↓
AI Processing
      ↓
Product Matching
      ↓
Recommendation
      ↓
Frontend Recommendation Screen
```

The frontend should clearly separate the survey interface from the final recommendation interface.

---

## 15. Error Handling

The frontend should provide clear messages when something goes wrong.

Examples include:

* Product is unavailable.
* AI recommendation cannot be generated.
* Required survey information is missing.
* Backend request fails.
* Product information cannot be loaded.

Error messages should be understandable to normal users and should avoid displaying technical error details unnecessarily.

---

## 16. Design Principles

When generating or modifying frontend components, follow these principles:

* Keep the interface clean.
* Prioritize usability.
* Keep the rental process simple.
* Make important actions clearly visible.
* Maintain consistent spacing and typography.
* Use reusable components.
* Keep the AI Assistant easy to access.
* Ensure responsive behavior.
* Avoid unnecessary complexity.
* Maintain consistency across all pages.

---

## 17. Development Guidelines for Kiro

When making changes to the Borrow Box frontend:

1. Understand the existing project structure before making changes.
2. Avoid unnecessarily modifying unrelated files.
3. Reuse existing components where possible.
4. Maintain consistency with the existing design.
5. Keep the code organized and readable.
6. Ensure new components are responsive.
7. Do not remove existing functionality unless specifically required.
8. Test the affected frontend functionality after making changes.
9. Ensure the UI matches the Borrow Box rental-platform requirements.
10. Keep the AI Rental Assistant experience simple and user-friendly.

---

## 18. Expected Result

The expected result of using Kiro is a frontend that represents the Borrow Box concept and provides the foundation for the rental platform.

The frontend should allow users to:

```text
Visit Borrow Box
      ↓
Explore the Platform
      ↓
Browse Products
      ↓
Use AI Rental Assistant
      ↓
Complete Requirement Survey
      ↓
View Personalized Recommendation
      ↓
Select Product
      ↓
Proceed With Rental
```

The frontend created with Kiro should provide a clear and scalable foundation for connecting the user interface with the Python/Node.js backend, MySQL database, and AI Rental Assistant.

---

## 19. Important Note

Kiro was used as a development assistant for implementing parts of the Borrow Box frontend based on the project's requirements.

The final implementation should be reviewed and tested to ensure that the generated frontend matches the actual project requirements and works correctly with the rest of the application.
