# Use an official Node.js runtime as the base image
FROM node:lts-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json into the container
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the application code into the container
COPY . .

# Build the production version of the app
RUN npm run build

# Expose the port your app runs on
EXPOSE 5173

# Define the command to run your app using the development server
CMD ["npm", "run", "dev", "--", "--port", "5173", "--host"]