# Use an official Node runtime as a parent image
FROM node:lts-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the working directory
COPY frontend/my-avatar-app/package*.json ./

# Install the app dependencies
RUN npm install

# Copy the rest of the app's source code to the working directory
COPY frontend/my-avatar-app /app/

# Build the app for production
RUN npm run build

# Copy package.json and package-lock.json for production dependencies
COPY frontend/my-avatar-app/package*.json ./

# Install only production dependencies
RUN npm install --only=production

# Define the port that the app will run on
ENV PORT=80

# Start the app using the serve script
CMD ["npm", "run", "serve"]