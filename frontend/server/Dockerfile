# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the server code to the working directory
COPY . .

# Expose the port the server will listen on
EXPOSE 3001

# Define the command to start the server
CMD ["npm", "start"]
